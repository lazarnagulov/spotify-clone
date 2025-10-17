import os
import json
import boto3
import uuid
from datetime import datetime

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.auth import require_role

from model.create_album_request import CreateAlbumRequest

dynamodb = boto3.client("dynamodb")
TABLE_NAME = os.environ["SONGS_TABLE"]
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

s3 = boto3.client("s3", region_name="eu-central-1")


@handle_lambda_exceptions
@require_role('admin')
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))
    request = CreateAlbumRequest.model_validate(body)

    album_id = str(uuid.uuid4())
    album_cover_path = f"covers/albums/{album_id}"
    timestamp = datetime.utcnow().isoformat() + "Z"

    album_item = {
        "PK": {"S": "ALBUM#" + album_id},
        "SK": {"S": "METADATA"},
        "type": {"S": "album"},
        "title": {"S": request.title},
        "artists": {"L": [{"S": artist} for artist in request.artists]},
        "genres": {"L": [{"S": genre} for genre in request.genres]},
        "year": {"N": str(request.year)},
        "coverPath": {"S": album_cover_path or ""},
        "coverType": {"S": request.cover_type or ""},
        "description": {"S": request.description or ""},
        "totalTracks": {"N": str(len(request.songs))},
        "createdAt": {"S": timestamp},
        "updatedAt": {"S": timestamp},
    }

    dynamodb.put_item(TableName=TABLE_NAME, Item=album_item)
    logger.info("Album metadata created", extra={"album_id": album_id})

    song_presigned_urls = []

    for i, song_data in enumerate(request.songs):
        song_id = str(uuid.uuid4())
        song_audio_path = f"songs/{song_id}"
        song_cover_path = f"covers/songs/{song_id}"

        album_song_item = {
            "PK": {"S": "ALBUM#" + album_id},
            "SK": {"S": "SONG#" + song_id},
            "type": {"S": "album_song"},
            "title": {"S": song_data.title},
            "trackNumber": {"N": str(i + 1)},
            "audioPath": {"S": song_audio_path or ""},
            "audioType": {"S": song_data.audio_type or ""},
            "duration": {"N": str(song_data.duration) if song_data.duration else "0"},
        }

        if song_data.cover_type:
            album_song_item["coverPath"] = {"S": song_cover_path or ""}
            album_song_item["coverType"] = {"S": song_data.cover_type or ""}

        dynamodb.put_item(TableName=TABLE_NAME, Item=album_song_item)

        song_metadata_item = {
            "PK": {"S": "SONG#" + song_id},
            "SK": {"S": "METADATA"},
            "type": {"S": "song"},
            "title": {"S": song_data.title},
            "artists": {"L": [{"S": artist} for artist in request.artists]},
            "genres": {"L": [{"S": genre} for genre in request.genres]},
            "album_id": {"S": album_id},
            "trackNumber": {"N": str(i + 1)},
            "description": {"S": song_data.description or ""},
            "audioPath": {"S": song_audio_path or ""},
            "audioType": {"S": song_data.audio_type or ""},
            "coverPath": {"S": song_cover_path or ""},
            "coverType": {"S": song_data.cover_type or ""},
            "duration": {"N": str(song_data.duration) if song_data.duration else "0"},
            "createdAt": {"S": timestamp},
            "updatedAt": {"S": timestamp},
        }

        dynamodb.put_item(TableName=TABLE_NAME, Item=song_metadata_item)

        presigned_audio_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": MEDIA_BUCKET,
                "Key": song_audio_path,
                "ContentType": song_data.audio_type,
            },
            ExpiresIn=3600
        )

        presigned_cover_url = None
        if song_data.cover_type:
            presigned_cover_url = s3.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": MEDIA_BUCKET,
                    "Key": song_cover_path,
                    "ContentType": song_data.cover_type,
                },
                ExpiresIn=3600
            )

        song_presigned_urls.append({
            "song_id": song_id,
            "title": song_data.title,
            "track_number": i + 1,
            "upload_url": presigned_audio_url,
            "cover_upload_url": presigned_cover_url
        })

        logger.info("Song created", extra={
            "album_id": album_id,
            "song_id": song_id,
            "track_number": i + 1
        })

    album_cover_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": MEDIA_BUCKET,
            "Key": album_cover_path,
            "ContentType": request.cover_type,
        },
        ExpiresIn=3600
    )

    logger.info("Album created successfully", extra={
        "album_id": album_id,
        "total_songs": len(request.songs)
    })

    return http_response(
        status_code=201,
        body={
            'album_id': album_id,
            'album_cover_upload_url': album_cover_url,
            'songs': song_presigned_urls
        }
    )