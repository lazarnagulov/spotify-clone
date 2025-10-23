import boto3
import json
import os
from datetime import datetime
from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions
from util.auth import require_role
from util.logger import logger

dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")
table = dynamodb.Table(os.environ["MUSIC_CATALOG"])
genre_relations_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
lambda_client = boto3.client("lambda")
s3 = boto3.client("s3", region_name="eu-central-1")

@handle_lambda_exceptions
@require_role("admin")
def handler(event, _context):
    song_id = event["pathParameters"]["id"]
    body = json.loads(event.get("body", "{}"))
    path_to_cover = f"covers/songs/{song_id}"
    path_to_audio = f"songs/{song_id}"

    logger.info("Editing song with ID: %s", song_id)
    existing_song = get_existing_song(song_id)
    if not existing_song:
        return http_response(404, {"message": "Song not found"})
    old_genres = set(existing_song.get("genres", [])) if existing_song else set()
    new_genres = set(body.get("genres", []))

    presigned_cover_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": MEDIA_BUCKET,
            "Key": path_to_cover,
            "ContentType": body.get("coverType", existing_song.get("coverType", "image/jpeg")),
        },
        ExpiresIn=3600
    )

    presigned_audio_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": MEDIA_BUCKET,
            "Key": path_to_audio,
            "ContentType": body.get("audioType", existing_song.get("audioType", "audio/mpeg")),
        },
        ExpiresIn=3600
    )

    logger.info("presigned url:", extra={"cover_url": presigned_cover_url, "audio_url": presigned_audio_url})

    update_song_metadata(song_id, body, existing_song)
    sync_genre_relations(existing_song, body, old_genres, new_genres)

    logger.info("Song updated successfully", extra={"song_id": song_id})
    return http_response(
        status_code=200,
        body={
            'coverUploadPresignedUrl': presigned_cover_url,
            'audioUploadPresignedUrl': presigned_audio_url
        }
    )

def get_existing_song(song_id: str) -> dict:
    result = table.get_item(Key={"PK": "SONG#" + song_id, "SK": "METADATA"})
    return result.get("Item")

def update_song_metadata(song_id: str, body: dict, existing_song) -> None:
    item = {
        "PK": "SONG#" + song_id,
        "SK": "METADATA",
        "title": body["title"],
        "genres": list(body.get("genres", [])),
        "artists": list(body.get("artists", [])),
        "description": body["description"],
        "updatedAt": datetime.utcnow().isoformat() + "Z",
        "type": "song",
        "mediaType": existing_song.get("mediaType", "audio/mpeg"),
        "audioPath": existing_song.get("audioPath", f"songs/{song_id}"),
        "coverPath": existing_song.get("coverPath", f"covers/songs/{song_id}"),
        "coverType": existing_song.get("coverType", "image/jpeg"),
        "audioType": existing_song.get("audioType", "audio/mpeg"),
        "createdAt": existing_song.get("createdAt"),
        "duration": existing_song.get("duration")
    }
    table.put_item(Item=item)

def sync_genre_relations(song: dict, body: dict, old_genres: set, new_genres: set) -> None:
    genres_to_add = new_genres - old_genres
    genres_to_remove = old_genres - new_genres
    genres_to_update = new_genres & old_genres

    title_changed = body["title"] != song.get("title")
    logger.info("Song title changed from: %s, to %s", body["title"], song.get("title"))

    with genre_relations_table.batch_writer() as batch:
        for genre in genres_to_remove:
            batch.delete_item(Key={"PK": genre, "SK": song['PK']})

    add_genres(genres_to_add, song, body)

    if title_changed:
        update_genres(genres_to_update, song, body)


def add_genres(genres, song, body):
    with genre_relations_table.batch_writer() as batch:
            for genre in genres:
                batch.put_item(
                    Item={
                        "PK": genre,
                        "SK": song['PK'].split('#')[1],
                        "Title": body["title"],
                        "CoverPath": body.get("coverPath", song.get("coverPath")),
                        "EntityType": "song"
                    }
                )

def update_genres(genres, song, body):
    with genre_relations_table.batch_writer() as batch:
        for genre in genres:
            batch.put_item(
                Item={
                    "PK": genre,
                    "SK": song['PK'].split('#')[1],
                    "Title": body["title"],
                    "EntityType": "song",
                    "CoverPath": body.get("coverPath", song.get("coverPath")),
                }
            )