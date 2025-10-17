import os
import boto3
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response

dynamodb = boto3.client("dynamodb")
dynamodb_resource = boto3.resource("dynamodb", region_name="eu-central-1")

TABLE_NAME = os.environ["SONGS_TABLE"]
ARTISTS_TABLE = os.environ.get("ARTISTS_TABLE", "Artists")
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
AWS_REGION = "eu-central-1"

deserializer = TypeDeserializer()


def deserialize_item(item):
    return {k: deserializer.deserialize(v) for k, v in item.items()}


def convert_decimals_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals_to_float(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals_to_float(item) for item in obj]
    return obj


def get_public_s3_url(key):
    return f"https://{MEDIA_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"


@handle_lambda_exceptions
def handler(event, _context):
    logger.info("Fetching home page data")

    artists_table = dynamodb_resource.Table(ARTISTS_TABLE)
    artists_scan = artists_table.scan()
    artists = []
    artists_names = {}

    for item in artists_scan.get("Items", [])[:5]:
        artist_id = item.get("PK")
        artist_name = item.get("name")
        artists.append({
            "id": artist_id,
            "name": artist_name,
            "genres": item.get("genres", [])
        })
        artists_names[artist_id] = artist_name

    logger.info(f"Found {len(artists)} artists", extra={"artists": artists_names})

    albums_response = dynamodb.scan(
        TableName=TABLE_NAME,
        FilterExpression="attribute_exists(#type) AND #type = :type AND SK = :metadata",
        ExpressionAttributeNames={"#type": "type"},
        ExpressionAttributeValues={
            ":type": {"S": "album"},
            ":metadata": {"S": "METADATA"}
        }
    )

    albums = []
    for item in albums_response.get("Items", [])[:5]:
        album_data = deserialize_item(item)
        cover_url = get_public_s3_url(album_data["coverPath"]) if album_data.get("coverPath") else None

        artist_ids = album_data.get("artists", [])
        artist_names = [artists_names.get(aid, aid) for aid in artist_ids]

        albums.append({
            "id": album_data["PK"],
            "title": album_data.get("title", ""),
            "artists": artist_names,
            "genres": album_data.get("genres", []),
            "year": album_data.get("year"),
            "cover_url": cover_url
        })

    logger.info(f"Found {len(albums)} albums")

    songs_response = dynamodb.scan(
        TableName=TABLE_NAME,
        FilterExpression="attribute_exists(#type) AND #type = :type AND SK = :metadata",
        ExpressionAttributeNames={"#type": "type"},
        ExpressionAttributeValues={
            ":type": {"S": "song"},
            ":metadata": {"S": "METADATA"}
        }
    )

    songs = []
    for item in songs_response.get("Items", [])[:5]:
        song_data = deserialize_item(item)

        cover_url = get_public_s3_url(song_data["coverPath"]) if song_data.get("coverType") else None

        artist_ids = song_data.get("artists", [])
        artist_names = [artists_names.get(aid, aid) for aid in artist_ids]

        songs.append({
            "id": song_data["PK"],
            "title": song_data.get("title", ""),
            "artists": artist_names,
            "cover_url": cover_url
        })

    logger.info(f"Found {len(songs)} songs")

    response_body = {
        "albums": convert_decimals_to_float(albums),
        "songs": convert_decimals_to_float(songs),
        "artists": convert_decimals_to_float(artists)
    }

    logger.info("Home page data fetched successfully")

    return http_response(200, response_body)
