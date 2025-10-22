import os
import boto3
from boto3.dynamodb.types import TypeDeserializer
from decimal import Decimal

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.auth import require_role


dynamodb = boto3.client("dynamodb")
dynamodb_resource = boto3.resource("dynamodb", region_name="eu-central-1")

feed_table = dynamodb_resource.Table(os.environ['USER_FEED'])
TABLE_NAME = os.environ["SONGS_TABLE"]
ARTISTS_TABLE = os.environ.get("ARTISTS_TABLE", "Artists")
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
AWS_REGION = "eu-central-1"

@handle_lambda_exceptions
@require_role('user', 'admin')
def handler(event, _context):
    logger.info("Fetching feed data")

    claims = event["requestContext"]["authorizer"]["claims"]
    user_id = claims["sub"]

    feed_record = get_user_feed(user_id)
    logger.info(f"Feed record: {feed_record}")

    if not feed_record or "feedItems" not in feed_record:
        return http_response(404, {"message": "No feed found for this user"})

    feed_items = feed_record["feedItems"]
    song_ids, album_ids, artist_ids = extract_feed_ids(feed_items)

    songs_data = batch_get_items(TABLE_NAME, song_ids)
    albums_data = batch_get_items(TABLE_NAME, album_ids)
    artists_data = batch_get_items(ARTISTS_TABLE, artist_ids)

    artists = map_artists(artists_data)[0]
    albums = map_albums(albums_data)
    songs = map_songs(songs_data)

    response_body = {
        "albums": convert_decimals_to_float(albums),
        "songs": convert_decimals_to_float(songs),
        "artists": convert_decimals_to_float(artists)
    }

    logger.info("Home page data fetched successfully")
    return http_response(200, response_body)


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


def get_public_s3_url(key: str) -> str:
    if not key:
        return None
    return f"https://{MEDIA_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"


def batch_get_items(table_name, ids):
    if not ids:
        return []

    logger.info(f"Fetching batch items for IDs: {ids}")
    keys = [{"PK": {"S": _id}, "SK": {"S": "METADATA"}} for _id in ids]

    response = dynamodb.batch_get_item(
        RequestItems={table_name: {"Keys": keys}}
    )
    return response["Responses"].get(table_name, [])


def get_user_feed(user_id: str):
    response = feed_table.get_item(
        Key={
            "PK": f"USER#{user_id}",
            "SK": "FEED"
        }
    )
    return response.get("Item")


def extract_feed_ids(feed_items):
    song_ids = [f"SONG#{item['id']}" for item in feed_items if item["type"] == "song"]
    album_ids = [f"ALBUM#{item['id']}" for item in feed_items if item["type"] == "album"]
    artist_ids = [item["id"] for item in feed_items if item["type"] == "artist"]
    return song_ids, album_ids, artist_ids


def map_artists(artists_data):
    artists = []
    artists_names = {}

    for item in artists_data:
        artist = deserialize_item(item)
        artist_id = artist.get("PK")
        artist_name = artist.get("name")

        artists.append({
            "id": artist_id,
            "name": artist_name,
            "genres": artist.get("genres", [])
        })

        artists_names[artist_id] = artist_name

    return artists, artists_names


def map_albums(albums_data):
    albums = []

    for item in albums_data:
        album = deserialize_item(item)
        cover_url = get_public_s3_url(album.get("coverPath"))

        artist_items = batch_get_items(ARTISTS_TABLE, album.get("artists"))
        artist_names = [artist["name"]["S"] for artist in artist_items]

        albums.append({
            "id": album["PK"],
            "title": album.get("title", ""),
            "artists": artist_names,
            "genres": album.get("genres", []),
            "year": album.get("year"),
            "cover_url": cover_url
        })

    return albums


def map_songs(songs_data):
    songs = []

    for item in songs_data:
        song = deserialize_item(item)
        cover_url = get_public_s3_url(song.get("coverPath"))

        artist_items = batch_get_items(ARTISTS_TABLE, song.get("artists"))
        artist_names = [artist["name"]["S"] for artist in artist_items]

        songs.append({
            "id": song["PK"],
            "title": song.get("title", ""),
            "artists": artist_names,
            "cover_url": cover_url
        })

    return songs
