import boto3
import os
from boto3.dynamodb.conditions import Key
from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions
from util.auth import require_role

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client("s3")

music_catalog_table = dynamodb.Table(os.environ["MUSIC_CATALOG"])
genre_relations_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]


@handle_lambda_exceptions
@require_role('admin')
def handler(event, _context):
    album_id = event['pathParameters']['id']
    album_pk = f'ALBUM#{album_id}'

    items = fetch_album_items(album_pk)
    if not items:
        return http_response(status_code=404, body={"error": "Album not found"})

    song_ids, genres = parse_album_items(items)

    delete_music_catalog_items(album_pk, items, song_ids)
    delete_genre_relations(genres, album_pk, song_ids)
    delete_media_from_s3(album_id, song_ids)

    return http_response(status_code=200, body={"message": "Album deleted successfully"})


def fetch_album_items(album_pk):
    response = music_catalog_table.query(
        KeyConditionExpression=Key("PK").eq(album_pk)
    )
    return response.get("Items", [])


def parse_album_items(items):
    song_ids = []
    genres = set()

    for item in items:
        sk = item["SK"]
        if sk.startswith("SONG#"):
            song_ids.append(sk.replace("SONG#", ""))
        elif sk == "METADATA":
            genres.update(item.get("genres", []))

    return song_ids, genres


def delete_music_catalog_items(album_pk, items, song_ids):
    with music_catalog_table.batch_writer() as batch:
        for item in items:
            batch.delete_item(Key={"PK": album_pk, "SK": item["SK"]})
        for song_id in song_ids:
            batch.delete_item(Key={"PK": f"SONG#{song_id}", "SK": "METADATA"})


def delete_genre_relations(genres, album_id, song_ids):
    with genre_relations_table.batch_writer() as batch:
        for genre in genres:
            batch.delete_item(Key={"PK": genre, "SK": album_id})
            for song_id in song_ids:
                batch.delete_item(Key={"PK": genre, "SK": f"SONG#{song_id}"})


def delete_media_from_s3(album_id, song_ids):
    objects_to_delete = [{'Key': f"covers/albums/{album_id}"}]

    for song_id in song_ids:
        objects_to_delete.extend([
            {'Key': f"songs/{song_id}"},
            {'Key': f"covers/songs/{song_id}"}
        ])

    if objects_to_delete:
        s3.delete_objects(
            Bucket=MEDIA_BUCKET,
            Delete={'Objects': objects_to_delete}
        )
