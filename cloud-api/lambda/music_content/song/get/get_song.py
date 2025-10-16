import os
from decimal import Decimal

import boto3
from boto3.dynamodb.types import TypeDeserializer

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response

dynamodb = boto3.client("dynamodb")
s3 = boto3.client("s3", region_name="eu-central-1")

TABLE_NAME = os.environ["SONGS_TABLE"]
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

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

@handle_lambda_exceptions
def handler(event, _context):
    song_id = event["pathParameters"]["id"]

    if not song_id.startswith("SONG#"):
        song_id = f"SONG#{song_id}"

    logger.info("Fetching song", extra={"song_id": song_id})

    response = dynamodb.get_item(
        TableName=TABLE_NAME,
        Key={
            "PK": {"S": song_id},
            "SK": {"S": "METADATA"}
        }
    )

    if "Item" not in response:
        return http_response(404, {"error": "Song not found"})

    song_data = deserialize_dynamodb_item(response["Item"])

    logger.info("Song data", extra={"song_data": song_data})

    audio_url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": MEDIA_BUCKET,
            "Key": song_data["audioPath"],
        },
        ExpiresIn=3600
    )

    cover_url = None
    if song_data.get("coverPath"):
        cover_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": MEDIA_BUCKET,
                "Key": song_data["coverPath"],
            },
            ExpiresIn=3600
        )

    album_info = None
    if song_data.get("albumId"):
        album_response = dynamodb.get_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": song_data["albumId"]},
                "SK": {"S": "METADATA"}
            }
        )

        if "Item" in album_response:
            album_data = deserialize_dynamodb_item(album_response["Item"])

            album_cover_url = s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": MEDIA_BUCKET,
                    "Key": album_data["coverPath"],
                },
                ExpiresIn=3600
            )

            album_info = {
                "id": song_data["albumId"],
                "title": album_data["title"],
                "year": album_data.get("year"),
                "cover_url": album_cover_url
            }

    song_response = {
        "id": song_id,
        "title": song_data["title"],
        "artists": song_data.get("artists", []),
        "genres": song_data.get("genres", []),
        "duration": song_data.get("duration", 0),
        "track_number": song_data.get("trackNumber"),
        "description": song_data.get("description", ""),
        "audio_url": audio_url,
        "cover_url": cover_url or (album_info["cover_url"] if album_info else None),
        "album": album_info,
        "created_at": song_data.get("createdAt"),
    }

    logger.info("Song fetched successfully", extra={"song_id": song_id})

    return http_response(200, convert_decimals_to_float(song_response))
