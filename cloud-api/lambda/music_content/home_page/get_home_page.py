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


# TODO: Personalize feed, this is just a sloooooow, boring example here!!!
@handle_lambda_exceptions
def handler(event, _context):
    logger.info("Fetching home page data")

    albums = []
    albums_response = dynamodb.scan(
        TableName=TABLE_NAME,
        FilterExpression="attribute_exists(#type) AND #type = :type AND SK = :metadata",
        ExpressionAttributeNames={"#type": "type"},
        ExpressionAttributeValues={
            ":type": {"S": "album"},
            ":metadata": {"S": "METADATA"}
        }
    )

    for item in albums_response.get("Items", [])[:5]:
        album_data = deserialize_item(item)

        cover_url = None
        if album_data.get("coverPath"):
            cover_url = get_public_s3_url(album_data["coverPath"])

        albums.append({
            "id": album_data["PK"],
            "title": album_data.get("title", ""),
            "artists": album_data.get("artists", []),
            "genres": album_data.get("genres", []),
            "year": album_data.get("year"),
            "cover_url": cover_url
        })

    logger.info(f"Found {len(albums)} albums")

    songs = []
    songs_response = dynamodb.scan(
        TableName=TABLE_NAME,
        FilterExpression="attribute_exists(#type) AND #type = :type AND SK = :metadata",
        ExpressionAttributeNames={"#type": "type"},
        ExpressionAttributeValues={
            ":type": {"S": "song"},
            ":metadata": {"S": "METADATA"}
        }
    )

    for item in songs_response.get("Items", [])[:5]:
        song_data = deserialize_item(item)

        cover_url = None
        if song_data.get("coverPath"):
            cover_url = get_public_s3_url(song_data["coverPath"])

        songs.append({
            "id": song_data["PK"],
            "title": song_data.get("title", ""),
            "artists": song_data.get("artists", []),
            "cover_url": cover_url
        })

    logger.info(f"Found {len(songs)} songs")

    artists_table = dynamodb_resource.Table(ARTISTS_TABLE)
    artists_scan = artists_table.scan()

    artists = []
    for item in artists_scan.get("Items", [])[:5]:
        artists.append({
            "id": item.get("PK"),
            "name": item.get("SK"),
            "genres": item.get("genres", [])
        })

    logger.info(f"Found {len(artists)} artists")

    response_body = {
        "albums": convert_decimals_to_float(albums),
        "songs": convert_decimals_to_float(songs),
        "artists": convert_decimals_to_float(artists)
    }

    logger.info("Home page data fetched successfully")

    return http_response(200, response_body)