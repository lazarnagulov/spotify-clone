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

dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")
table = dynamodb.Table(os.environ["MUSIC_CATALOG"])
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

s3 = boto3.client("s3", region_name="eu-central-1")
lambda_client = boto3.client("lambda")

@handle_lambda_exceptions
@require_role('admin')
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))
    request = CreateAlbumRequest.model_validate(body)

    album_id = str(uuid.uuid4())
    album_cover_path = f"covers/albums/{album_id}"
    timestamp = datetime.utcnow().isoformat() + "Z"

    album_item = {
        "PK": "ALBUM#" + album_id,
        "SK": "METADATA",
        "type": "album",
        "title": request.title,
        "artists": request.artists,
        "genres": request.genres,
        "year": request.year,
        "coverPath": album_cover_path,
        "coverType": request.cover_type,
        "description": request.description or "",
        "totalTracks": len(request.songs),
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }

    table.put_item(Item=album_item)
    logger.info("Album metadata created", extra={"album_id": album_id})

    song_presigned_urls = []
    songs = []

    for i, song_data in enumerate(request.songs):
        song_id = str(uuid.uuid4())
        song_audio_path = f"songs/{song_id}"
        song_cover_path = f"covers/songs/{song_id}"

        album_song_item = {
            "PK": "ALBUM#" +  album_id,
            "SK": "SONG#" + song_id,
            "type": "album_song",
            "title": song_data.title,
            "trackNumber": i + 1,
            "audioPath": song_audio_path,
            "audioType": song_data.audio_type,
            "duration": song_data.duration or 0,
        }

        if song_data.cover_type:
            album_song_item["coverPath"] = song_cover_path
            album_song_item["coverType"] = song_data.cover_type

        table.put_item(Item=album_song_item)

        song_metadata_item = {
            "PK": "SONG#" + song_id,
            "SK": "METADATA",
            "type": "song",
            "title": song_data.title,
            "artists": request.artists,
            "genres": request.genres,
            "coverPath": song_cover_path,
            "coverType": song_data.cover_type,
            "album_id": album_id,
            "trackNumber": i + 1,
            "description": song_data.description or "",
            "audioPath": song_audio_path,
            "audioType": song_data.audio_type,
            "duration": song_data.duration or 0,
            "createdAt": timestamp,
            "updatedAt": timestamp,
        }

        songs.append(song_metadata_item)
        table.put_item(Item=song_metadata_item)

        presigned_audio_url = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": MEDIA_BUCKET,
                "Key": song_audio_path,
                "ContentType": song_data.audio_type,
            },
            ExpiresIn=3600,
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

    update_genre_relations_table(request, album_id, album_cover_path, songs)
    update_artist_relations_table(request, album_id, album_cover_path, songs)
    notify_subscribers(request)

    return http_response(
        status_code=201,
        body={
            "album_id": album_id,
            "album_cover_upload_url": album_cover_url,
            "songs": song_presigned_urls,
        },
    )

def update_artist_relations_table(request, album_id, path_to_cover, songs):
    artists_table=dynamodb.Table(os.environ['ARTIST_TABLE'])

    with artists_table.batch_writer() as batch:
        for artist in request.artists:
            batch.put_item(
                Item={
                    "PK": artist,
                    "SK": f"ALBUM#{album_id}",
                    "EntityType": "album",
                    "Title": request.title,
                    "CoverPath": path_to_cover,
                }
            )

            for song in songs:
                batch.put_item(
                    Item={
                        "PK": artist,
                        "SK": song['PK'],
                        "EntityType": "song",
                        "Title": song["title"],
                        "CoverPath": song["coverPath"]
                    }
                )

def update_genre_relations_table(request, album_id, path_to_cover, songs):
    genre_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])

    logger.info("Updating genre relations", extra={"songs": songs})

    with genre_table.batch_writer() as batch:
        for genre in request.genres:
            batch.put_item(
                Item={
                    "PK": genre,
                    "SK": album_id,
                    "EntityType": "album",
                    "Title": request.title,
                    "CoverPath": path_to_cover,
                    "ArtistNames": request.artists,
                }
            )

            for song in songs:
                batch.put_item(
                    Item={
                        "PK": genre,
                        "SK": song["PK"],
                        "EntityType": "song",
                        "Title": song["title"],
                        "CoverPath": song["coverPath"],
                        "ArtistNames": request.artists,
                    }
                )

    logger.info(
        "Genre relations updated successfully",
        extra={
            "album_id": album_id,
            "total_genres": len(request.genres),
            "total_songs": len(songs),
        },
    )


def notify_subscribers(request):
    lambda_client.invoke(
        FunctionName=os.environ["NOTIFY_SUBSCRIBERS_FUNCTION"],
        InvocationType="Event",
        Payload=json.dumps({
            "event_type": "album",
            "artist_ids": request.artists,
            "album_title": request.title,
            "songs": [s.title for s in request.songs],
            "genres": request.genres
        })
    )

    logger.info(
        "Sending notification to subscribers",
        extra={
            "artist_id": request.artists,
            "album_title": request.title,
            "genres": request.genres
        },
    )
