import os
import json
import boto3
import uuid
from datetime import datetime

from util.auth import require_role
from util.http_response import http_response
from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from model.create_song_request import CreateSongRequest

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["MUSIC_CATALOG"])

MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

s3 = boto3.client("s3", region_name="eu-central-1")


@handle_lambda_exceptions
@require_role('admin')
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))
    request = CreateSongRequest.model_validate(body)
    song_id = str(uuid.uuid4())
    path_to_cover = f"covers/songs/{song_id}"
    path_to_audio = f"songs/{song_id}"

    item = {
        "PK": "SONG#" + song_id,
        "SK": "METADATA",
        "title": request.title,
        "genres": request.genres,
        "artists": request.artists,
        "albumId": request.album_id or "",
        "coverPath": path_to_cover,
        "audioPath": path_to_audio,
        "coverType": request.cover_type,
        "audioType": request.audio_type,
        "description": request.description,
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "updatedAt": datetime.utcnow().isoformat() + "Z",
    }

    table.put_item(Item=item)
    logger.info("Song metadata saved", extra={"song_id": song_id, "data": item})

    presigned_cover_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": MEDIA_BUCKET,
            "Key": path_to_cover,
        },
        ExpiresIn=3600
    )

    presigned_audio_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": MEDIA_BUCKET,
            "Key": path_to_audio,
        },
        ExpiresIn=3600
    )

    update_genre_relations_table(request, song_id, path_to_cover)

    return http_response(
        status_code=201,
        body={
            'coverUploadPresignedUrl': presigned_cover_url,
            'audioUploadPresignedUrl': presigned_audio_url
        }
    )

def update_genre_relations_table(request, song_id, path_to_cover):
    genre_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])

    for genre in request.genres:
        genre_table.put_item(
            Item={
                "PK": genre,
                "SK": song_id,
                "EntityType": "song",
                "Title": request.title,
                "CoverPath": path_to_cover,
                "ArtistNames": request.artists
            }
        )