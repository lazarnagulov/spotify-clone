import os
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response


dynamodb = boto3.client("dynamodb")
dynamodb_resource = boto3.resource("dynamodb")
table = dynamodb_resource.Table(os.environ["SONGS_TABLE"])
artists_table_name = os.environ["ARTISTS_TABLE"]

TABLE_NAME = os.environ["SONGS_TABLE"]
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
AWS_REGION = "eu-central-1"

deserializer = TypeDeserializer()


def deserialize_item(item):
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
        artists_table_name: {
            "Keys": [{"PK": {"S": artist_id}, "SK": {"S": "METADATA"}} for artist_id in artist_ids],
            "ProjectionExpression": "PK, #n",
            "ExpressionAttributeNames": {"#n": "name"}
        }
    }

    response = dynamodb.batch_get_item(RequestItems=request_items)
    artists = response.get("Responses", {}).get(artists_table_name, [])

    artist_name_map = {}
    for artist in artists:
        artist_data = deserialize_item(artist)
        artist_name_map[artist_data["PK"]] = artist_data.get("name", "Unknown")

    return artist_name_map


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

    cover_url = get_public_s3_url(album_data["coverPath"]) if album_data.get("coverPath") else None

    query_response = table.query(
        KeyConditionExpression=Key("PK").eq(album_id) & Key("SK").begins_with("SONG#")
    )

    songs = []
    for item in query_response.get("Items", []):
        song_audio_url = get_public_s3_url(item["audioPath"])
        song_cover_url = get_public_s3_url(item["coverPath"]) if item.get("coverPath") else None

        song_item = {
            "id": item["SK"],
            "title": item["title"],
            "track_number": int(item.get("trackNumber", 0)),
            "duration": float(item.get("duration", 0)),
            "audio_url": song_audio_url,
        }

        if song_cover_url:
            song_item["cover_url"] = song_cover_url

        songs.append(song_item)

    songs.sort(key=lambda s: s["track_number"])

    artist_ids = album_data.get("artists", [])
    artist_name_map = fetch_artist_names(artist_ids)
    artist_names = [artist_name_map.get(aid, "Unknown") for aid in artist_ids]

    album_response_body = {
        "id": album_id,
        "title": album_data["title"],
        "artists": artist_names,
        "genres": album_data.get("genres", []),
        "year": album_data.get("year"),
        "description": album_data.get("description", ""),
        "coverUrl": cover_url,
        "songs": songs,
        "created_at": album_data.get("created_at"),
        "artist_ids": artist_ids
    }

    album_response_body = convert_decimals_to_float(album_response_body)

    logger.info("Album fetched successfully", extra={
        "album_id": album_id,
        "song_count": len(songs)
    })

    return http_response(200, album_response_body)
