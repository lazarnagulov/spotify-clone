import os
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
            "Key": song_data["pathToAudio"],
        },
        ExpiresIn=3600
    )

    cover_url = None
    if song_data.get("pathToCover"):
        cover_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": MEDIA_BUCKET,
                "Key": song_data["pathToCover"],
            },
            ExpiresIn=3600
        )

    album_info = None
    if song_data.get("album_id"):
        album_response = dynamodb.get_item(
            TableName=TABLE_NAME,
            Key={
                "PK": {"S": song_data["album_id"]},
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
                "id": song_data["album_id"],
                "title": album_data["title"],
                "year": album_data.get("year"),
                "cover_url": album_cover_url
            }

    # related_songs = []
    # if song_data.get("artists") and len(song_data["artists"]) > 0:
    #     # Query za pesme istog umetnika (ovo zahteva GSI, zasad mock)
    #     # TODO: Implementirati Query sa GSI za artist-song-index
    #     pass

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
        "created_at": song_data.get("created_at"),
        # "related_songs": related_songs
    }

    logger.info("Song fetched successfully", extra={"song_id": song_id})

    return http_response(200, song_response)
