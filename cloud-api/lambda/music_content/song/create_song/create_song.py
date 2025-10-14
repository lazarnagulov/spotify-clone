import os
import json
import boto3
import uuid
from datetime import datetime

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from model.create_song_request import CreateSongRequest

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["SONGS_TABLE"])

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGE_BUCKET = os.environ["IMAGE_BUCKET"]

s3 = boto3.client("s3", region_name="eu-central-1")


@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))
    request = CreateSongRequest.model_validate(body)
    song_id = str(uuid.uuid4())
    path_to_cover = f"images/{song_id}"
    path_to_audio = f"songs/{song_id}"

    item = {
        "PK": "SONG#" + song_id,
        "SK": "METADATA",
        "title": request.title,
        "genres": request.genres,
        "artists": request.artists if request.artists else ["Unknown"],
        "album_id": request.album_id or "",
        "pathToCover": path_to_cover,
        "pathToAudio": path_to_audio,
        "coverType": request.cover_type,
        "audio_type": request.audio_type,
        "description": request.description,
        "created_at": datetime.utcnow().isoformat() + "Z",
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }

    table.put_item(Item=item)
    logger.info("Song metadata saved", extra={"song_id": song_id, "data": item})

    presigned_cover_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": IMAGE_BUCKET,
            "Key": path_to_cover,
        },
        ExpiresIn=3600
    )

    presigned_audio_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": AUDIO_BUCKET,
            "Key": path_to_audio,
        },
        ExpiresIn=3600
    )

    return {
        'statusCode': 201,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        },
        'body': json.dumps({
            'coverUploadPresignedUrl': presigned_cover_url,
            'audioUploadPresignedUrl': presigned_audio_url
        })
    }
