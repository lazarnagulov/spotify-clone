import boto3
import json
import os
from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions
from util.auth import require_role

dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genre_relations_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])


@handle_lambda_exceptions
@require_role("admin")
def handler(event, _context):
    artist_id = event["pathParameters"]["id"]
    body = json.loads(event.get("body", "{}"))

    existing_artist = get_existing_artist(artist_id)
    old_genres = set(existing_artist.get("genres", [])) if existing_artist else set()
    new_genres = set(body.get("genres", []))

    update_artist_metadata(artist_id, body)
    sync_genre_relations(existing_artist, body, old_genres, new_genres)

    return http_response(200,{"message": "Artist successfully edited"})


def get_existing_artist(artist_id: str) -> dict:
    result = artists_table.get_item(Key={"PK": artist_id, "SK": "METADATA"})
    return result.get("Item")


def update_artist_metadata(artist_id: str, body: dict) -> None:
    artists_table.put_item(
        Item={
            "PK": artist_id,
            "SK": "METADATA",
            "name": body["name"],
            "bio": body["bio"],
            "genres": list(body.get("genres", [])),
        }
    )


def sync_genre_relations(artist: dict, body: dict, old_genres: set, new_genres: set) -> None:
    genres_to_add = new_genres - old_genres
    genres_to_remove = old_genres - new_genres
    genres_to_update = new_genres & old_genres

    name_changed = body["name"] != artist.get("name")
    bio_changed = body["bio"] != artist.get("bio")

    with genre_relations_table.batch_writer() as batch:
        for genre in genres_to_remove:
            batch.delete_item(Key={"PK": genre, "SK": artist['PK']})

    with genre_relations_table.batch_writer() as batch:
        for genre in genres_to_add:
            batch.put_item(
                Item={
                    "PK": genre,
                    "SK": artist['PK'],
                    "Name": body["name"],
                    "bio": body["bio"],
                }
            )

    if name_changed or bio_changed:
        for genre in genres_to_update:
            genre_relations_table.update_item(
                Key={"PK": genre, "SK": artist['PK']},
                UpdateExpression="SET #N = :name, bio = :bio",
                ExpressionAttributeNames={"#N": "Name"},
                ExpressionAttributeValues={
                    ":name": body["name"],
                    ":bio": body["bio"],
                },
            )
