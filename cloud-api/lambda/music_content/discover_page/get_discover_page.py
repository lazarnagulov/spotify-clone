import os
import boto3
import json
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.conditions import Key

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.auth import require_role

AWS_REGION = "eu-central-1"
GENRE_RELATIONS_TABLE = os.environ["GENRE_RELATIONS_TABLE"]
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

dynamodb_resource = boto3.resource("dynamodb", region_name=AWS_REGION)

def get_public_s3_url(key):
    return f"https://{MEDIA_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"

@handle_lambda_exceptions
@require_role('user', 'admin')
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))
    genre = body.get("genre")

    if not genre:
        return http_response(400, {"error": "Missing 'genre' in request body"})

    logger.info(f"Fetching data for genre: {genre}")

    table = dynamodb_resource.Table(GENRE_RELATIONS_TABLE)

    response = table.query(
        KeyConditionExpression=Key("PK").eq(genre)
    )

    items = response.get("Items", [])

    songs = []
    albums = []
    artists = []

    for item in items:
        entity_type = item.get("EntityType")

        if entity_type == "song":
            songs.append({
                "id": item.get("SK"),
                "title": item.get("Title"),
                "artists": item.get("ArtistNames", []),
                "cover_url": get_public_s3_url(item["CoverPath"]) if item.get("CoverPath") else None
            })
        elif entity_type == "album":
            albums.append({
                "id": item.get("SK"),
                "title": item.get("Title"),
                "artists": item.get("ArtistNames", []),
                "cover_url": get_public_s3_url(item["CoverPath"]) if item.get("CoverPath") else None
            })
        elif entity_type == "artist":
            artists.append({
                "id": item.get("SK"),
                "name": item.get("Name")
            })

    response_body = {
        "genre": genre,
        "songs": songs,
        "albums": albums,
        "artists": artists
    }

    logger.info(f"Genre '{genre}' data fetched successfully")

    return http_response(200, response_body)