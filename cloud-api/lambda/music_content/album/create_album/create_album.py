import os
import json
import boto3
import uuid
from datetime import datetime

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from model.create_album_request import CreateAlbumRequest

dynamodb = boto3.client("dynamodb")
TABLE_NAME = os.environ["SONGS_TABLE"]
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

s3 = boto3.client("s3", region_name="eu-central-1")


@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))
    request = CreateAlbumRequest.model_validate(body)

    album_id = "ALBUM#" + str(uuid.uuid4())
    album_cover_path = f"covers/albums/{album_id}"
    timestamp = datetime.utcnow().isoformat() + "Z"

    album_item = {
        "PK": {"S": album_id},
        "SK": {"S": "METADATA"},
        "type": {"S": "album"},
        "title": {"S": request.title},
        "artists": {"L": [{"S": artist} for artist in request.artists]},
        "genres": {"L": [{"S": genre} for genre in request.genres]},
        "year": {"N": str(request.year)},
        "coverPath": {"S": album_cover_path},
        "coverType": {"S": request.cover_type},
        "description": {"S": request.description or ""},
        "totalTracks": {"N": str(len(request.songs))},
        "created_at": {"S": timestamp},
        "updated_at": {"S": timestamp},
    }

    dynamodb.put_item(TableName=TABLE_NAME, Item=album_item)
    logger.info("Album metadata created", extra={"album_id": album_id})

    song_presigned_urls = []

    for i, song_data in enumerate(request.songs):
        song_id = "SONG#" + str(uuid.uuid4())
        audio_path = f"songs/{song_id}"

        album_song_item = {
            "PK": {"S": album_id},
            "SK": {"S": song_id},
            "type": {"S": "album_song"},
            "title": {"S": song_data.title},
            "trackNumber": {"N": str(i + 1)},
            "pathToAudio": {"S": audio_path},
            "audioType": {"S": song_data.audio_type},
            "duration": {"N": str(song_data.duration) if song_data.duration else "0"},
        }

        dynamodb.put_item(TableName=TABLE_NAME, Item=album_song_item)

        song_metadata_item = {
            "PK": {"S": song_id},
            "SK": {"S": "METADATA"},
            "type": {"S": "song"},
            "title": {"S": song_data.title},
            "artists": {"L": [{"S": artist} for artist in request.artists]},
            "genres": {"L": [{"S": genre} for genre in request.genres]},
            "album_id": {"S": album_id},
            "trackNumber": {"N": str(i + 1)},
            "description": {"S": song_data.description or ""},
            "pathToAudio": {"S": audio_path},
            "audioType": {"S": song_data.audio_type},
            "duration": {"N": str(song_data.duration) if song_data.duration else "0"},
            "created_at": {"S": timestamp},
            "updated_at": {"S": timestamp},
        }

        dynamodb.put_item(TableName=TABLE_NAME, Item=song_metadata_item)

        presigned_audio_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": MEDIA_BUCKET,
                "Key": audio_path,
                "ContentType": song_data.audio_type,
            },
            ExpiresIn=3600
        )

        song_presigned_urls.append({
            "song_id": song_id,
            "title": song_data.title,
            "track_number": i + 1,
            "upload_url": presigned_audio_url
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

    return {
        'statusCode': 201,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        },
        'body': json.dumps({
            'album_id': album_id,
            'album_cover_upload_url': album_cover_url,
            'songs': song_presigned_urls
        })
    }