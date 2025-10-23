import os
import boto3
from boto3.dynamodb.conditions import Key
from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.auth import require_role

AWS_REGION = "eu-central-1"
GENRE_RELATIONS_TABLE = os.environ["GENRE_RELATIONS_TABLE"]
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]

dynamodb_resource = boto3.resource("dynamodb", region_name=AWS_REGION)


def get_public_s3_url(key: str):
    return f"https://{MEDIA_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"


@handle_lambda_exceptions
@require_role('user', 'admin')
def handler(event, _context):
    genre = event["pathParameters"].get("genre") if event.get("pathParameters") else None

    if not genre:
        return http_response(400, {"error": "Missing 'genre' in path parameters"})

    logger.info(f"Fetching data for genre: {genre}")

    table = dynamodb_resource.Table(GENRE_RELATIONS_TABLE)

    response = table.query(KeyConditionExpression=Key("PK").eq(genre))
    items = response.get("Items", [])

    songs, albums, artists = [], [], []

    for item in items:
        entity_type = item.get("EntityType")

        cover_path = item.get("CoverPath")

        if entity_type == "song":
            songs.append({
                "id": item.get("SK"),
                "title": item.get("Title", ""),
                "artists": item.get("ArtistNames", []),
                "cover_url": get_public_s3_url(cover_path) if cover_path else None
            })

        elif entity_type == "album":
            albums.append({
                "id": "ALBUM#" + item.get("SK"),
                "title": item.get("Title", ""),
                "artists": item.get("ArtistNames", []),
                "coverUrl": get_public_s3_url(cover_path) if cover_path else None
            })

        elif entity_type == "artist":
            artists.append({
                "id": item.get("SK"),
                "name": item.get("Name", "")
            })

    response_body = {
        "genre": genre,
        "songs": songs,
        "albums": albums,
        "artists": artists
    }

    logger.info(
        f"Fetched {len(songs)} songs, {len(albums)} albums, and {len(artists)} artists for genre '{genre}'"
    )

    return http_response(200, response_body)