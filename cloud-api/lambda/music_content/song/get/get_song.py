import os
import json
from decimal import Decimal
import boto3
from boto3.dynamodb.types import TypeDeserializer

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response

dynamodb = boto3.client("dynamodb")
TABLE_NAME = os.environ["SONGS_TABLE"]
ARTISTS_TABLE = os.environ["ARTISTS_TABLE"]
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
AWS_REGION = "eu-central-1"

deserializer = TypeDeserializer()


def deserialize_dynamodb_item(item):
    return {k: deserializer.deserialize(v) for k, v in item.items()}


def convert_decimals_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals_to_float(item) for item in obj]
    return obj


def get_public_s3_url(key):
    return f"https://{MEDIA_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"


def fetch_artist_names(artist_ids):
    if not artist_ids:
        return {}

    request_items = {
        ARTISTS_TABLE: {
            "Keys": [{"PK": {"S": aid}, "SK": {"S": "METADATA"}} for aid in artist_ids],
            "ProjectionExpression": "PK, #n",
            "ExpressionAttributeNames": {"#n": "name"}
        }
    }

    response = dynamodb.batch_get_item(RequestItems=request_items)
    artists = response.get("Responses", {}).get(ARTISTS_TABLE, [])

    artist_name_map = {}
    for artist in artists:
        artist_data = deserialize_dynamodb_item(artist)
        artist_name_map[artist_data["PK"]] = artist_data.get("name", "Unknown")

    return artist_name_map


def get_transcription(song_key: str):
    s3 = boto3.client("s3")
    clean_key = song_key.replace("songs/", "")
    transcription_key = f"transcriptions/{clean_key}.json"
    logger.info(f"Looking for transcription: {transcription_key}")

    try:
        response = s3.get_object(Bucket=MEDIA_BUCKET, Key=transcription_key)
        content = response["Body"].read().decode("utf-8")
        transcript_json = json.loads(content)

        segments = transcript_json.get("results", {}).get("audio_segments", [])
        if not segments:
            logger.info("No audio_segments found, falling back to items parsing")
            return None

        lines = [seg.get("transcript", "").strip() for seg in segments if seg.get("transcript")]
        return "\n".join(lines) if lines else None

    except s3.exceptions.NoSuchKey:
        logger.info(f"No transcription found for {transcription_key}")
        return None


@handle_lambda_exceptions
def handler(event, _context):
    song_id = event["pathParameters"]["id"]
    if not song_id.startswith("SONG#"):
        song_id = f"SONG#{song_id}"

    logger.info("Fetching song", extra={"song_id": song_id})

    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={"PK": {"S": song_id}, "SK": {"S": "METADATA"}}
    )

    if "Item" not in response:
        return http_response(404, {"error": "Song not found"})

    song_data = deserialize_dynamodb_item(response["Item"])

    logger.info("Song data", extra={"song_data": song_data})

    artist_ids = song_data.get("artists", [])
    artist_name_map = fetch_artist_names(artist_ids)
    artist_names = [artist_name_map.get(aid, aid) for aid in artist_ids]

    audio_url = get_public_s3_url(song_data["audioPath"])

    cover_url = None
    if song_data.get("coverType"):
        cover_url = get_public_s3_url(song_data["coverPath"])

    song_response = {
        "id": song_id,
        "title": song_data["title"],
        "artists": artist_names,
        "genres": song_data.get("genres", []),
        "duration": song_data.get("duration", 0),
        "track_number": song_data.get("trackNumber"),
        "description": song_data.get("description", ""),
        "audio_url": audio_url,
        "cover_url": cover_url,
        "created_at": song_data.get("created_at"),
        "transcript": get_transcription(song_data["audioPath"])
    }

    logger.info("Song fetched successfully", extra={"song_id": song_id})

    return http_response(200, convert_decimals_to_float(song_response))
