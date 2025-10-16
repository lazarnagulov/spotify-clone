import os
import json
import boto3
import uuid
from datetime import datetime

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response

from auth import require_role
from model.create_album_request import CreateAlbumRequest

dynamodb = boto3.client("dynamodb")
table = dynamodb.Table(os.environ["MUSIC_CATALOG"])
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

s3 = boto3.client("s3", region_name="eu-central-1")


@handle_lambda_exceptions
@require_role('admin')
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

    table.put_item(Item=album_item)
    logger.info("Album metadata created", extra={"album_id": album_id})

    song_presigned_urls = []
    songs = []

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

        table.put_item(Item=album_song_item)

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

        songs.append(song_metadata_item)

        table.put_item(Item=song_metadata_item)

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

    update_genre_relations_table(request, album_id, album_cover_path, songs)

    return http_response(
        status_code=201,
        body={
            'album_id': album_id,
            'album_cover_upload_url': album_cover_url,
            'songs': song_presigned_urls
        }
    )

def update_genre_relations_table(request, album_id, path_to_cover, songs):
    genre_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])

    for genre in request.genres:
        genre_table.put_item(
            Item={
                "Genre": genre,
                "EntityId": album_id,
                "EntityType": "album",
                "Title": request.title,
                "CoverPath": path_to_cover,
                "ArtistNames": request.artists
            }
        )
        for song in songs:
            genre_table.put_item(
                Item={
                    "Genre": genre,
                    "EntityId": song["PK"]["S"],
                    "EntityType": "song",
                    "Title": song["title"]["S"],
                    "CoverPath": path_to_cover, # TODO: change to song cover path if exists
                    "ArtistNames": request.artists
                }
            )