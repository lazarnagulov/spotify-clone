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

lambda_client = boto3.client("lambda")
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
        "coverPath": path_to_cover,
        "audioPath": path_to_audio,
        "coverType": request.cover_type,
        "audioType": request.audio_type,
        "description": request.description,
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "updatedAt": datetime.utcnow().isoformat() + "Z",
        "type": "song",
    }

    table.put_item(Item=item)
    logger.info("Song metadata saved", extra={"song_id": song_id, "data": item})

    presigned_cover_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": MEDIA_BUCKET,
            "Key": path_to_cover,
            "ContentType": request.cover_type,
        },
        ExpiresIn=3600
    )

    presigned_audio_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": MEDIA_BUCKET,
            "Key": path_to_audio,
            "ContentType": request.audio_type,
        },
        ExpiresIn=3600
    )

    update_genre_relations_table(request, song_id, path_to_cover)
    update_artist_relations_table(request, song_id, path_to_cover)
    notify_subscribers(request)

    return http_response(
        status_code=201,
        body={
            'coverUploadPresignedUrl': presigned_cover_url,
            'audioUploadPresignedUrl': presigned_audio_url
        }
    )


def update_genre_relations_table(request, song_id, path_to_cover):
    genre_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])

    with genre_table.batch_writer() as batch:
        for genre in request.genres:
            batch.put_item(
                Item={
                    "PK": genre,
                    "SK": song_id,
                    "EntityType": "song",
                    "Title": request.title,
                    "CoverPath": path_to_cover,
                    "ArtistNames": request.artists
                }
            )

def update_artist_relations_table(request, song_id, path_to_cover):
    artists_table=dynamodb.Table(os.environ['ARTIST_TABLE'])
    with artists_table.batch_writer() as batch:
        for artist in request.artists:
            batch.put_item(
                Item={
                    "PK": artist,
                    "SK": f"SONG#{song_id}",
                    "EntityType": "song",
                    "Title": request.title,
                    "CoverPath": path_to_cover,
                }
            )

def notify_subscribers(request):
    lambda_client.invoke(
        FunctionName=os.environ["NOTIFY_SUBSCRIBERS_FUNCTION"],
        InvocationType="Event",
        Payload=json.dumps({
            "event_type": "song",
            "artist_ids": request.artists,
            "song_title": request.title,
            "genres": request.genres
        })
    )

    logger.info(
        "Sending notification to subscribers",
        extra={
            "artist_ids": request.artists,
            "song_title": request.title,
            "genres": request.genres
        },
    )
