import os
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response

dynamodb = boto3.client("dynamodb")
dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table(os.environ["SONGS_TABLE"])
s3 = boto3.client("s3", region_name="eu-central-1")

TABLE_NAME = os.environ["SONGS_TABLE"]
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

deserializer = TypeDeserializer()


def deserialize_item(item):
    return {k: deserializer.deserialize(v) for k, v in item.items()}


from decimal import Decimal

def convert_decimals_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals_to_float(item) for item in obj]
    return obj

@handle_lambda_exceptions
def handler(event, _context):
    album_id = event["pathParameters"]["id"]
    if not album_id.startswith("ALBUM#"):
        album_id = f"ALBUM#{album_id}"

    logger.info("Fetching album", extra={"album_id": album_id})

    album_response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={"PK": {"S": album_id}, "SK": {"S": "METADATA"}}
    )

    if "Item" not in album_response:
        return http_response(404, {"error": "Album not found"})

    album_data = deserialize_item(album_response["Item"])
    logger.info("Album metadata retrieved", extra={"album_id": album_id})

    cover_url = None
    if album_data.get("coverPath"):
        cover_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": MEDIA_BUCKET,
                "Key": album_data["coverPath"]
            },
            ExpiresIn=3600
        )

    query_response = table.query(
        KeyConditionExpression=Key("PK").eq(album_id) & Key("SK").begins_with("SONG#")
    )
    songs = []

    for item in query_response.get("Items", []):
        song_data = item
        song_audio_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": MEDIA_BUCKET,
                "Key": song_data["pathToAudio"],
            },
            ExpiresIn=3600
        )

        songs.append({
            "id": song_data["SK"],
            "title": song_data["title"],
            "track_number": int(song_data.get("trackNumber", 0)),
            "duration": float(song_data.get("duration", 0)),
            "audio_url": song_audio_url
        })

    songs.sort(key=lambda s: s["track_number"])

    album_response_body = {
        "id": album_id,
        "title": album_data["title"],
        "artists": album_data.get("artists", []),
        "genres": album_data.get("genres", []),
        "year": album_data.get("year"),
        "description": album_data.get("description", ""),
        "imageUrl": cover_url,
        "songs": songs,
        "created_at": album_data.get("created_at"),
    }

    album_response_body = convert_decimals_to_float(album_response_body)

    logger.info("Album fetched successfully", extra={
        "album_id": album_id,
        "song_count": len(songs)
    })

    return http_response(200, album_response_body)

