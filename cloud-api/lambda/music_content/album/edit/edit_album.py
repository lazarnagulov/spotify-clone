import os
import json
import boto3
from datetime import datetime

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.auth import require_role

dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")
table = dynamodb.Table(os.environ["MUSIC_CATALOG"])
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
genre_relations_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])

s3 = boto3.client("s3", region_name="eu-central-1")
lambda_client = boto3.client("lambda")

@handle_lambda_exceptions
@require_role('admin')
def handler(event, _context):
  album_id = event["pathParameters"]["id"]
  body = json.loads(event.get("body", "{}"))
  path_to_cover = f"covers/albums/{album_id}"

  logger.info("Editing album with ID: %s", album_id)
  existing_album = get_existing_album(album_id)
  if not existing_album:
      return http_response(404, {"message": "Album not found"})
  
  if "coverType" in body:
    presigned_cover_url = s3.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": MEDIA_BUCKET,
            "Key": path_to_cover,
            "ContentType": body.get("coverType", existing_album.get("coverType", "image/jpeg")),
        },
        ExpiresIn=3600
    )
  else:
    presigned_cover_url = None

  sync_genre_relations(existing_album, body, set(existing_album.get("genres", [])), set(body.get("genres", [])))
  sync_artist_relations_table(existing_album, body)

  logger.info("presigned url:", extra={"cover_url": presigned_cover_url})
  update_album_metadata(album_id, body, existing_album)
  logger.info("Album updated successfully", extra={"album_id": album_id})
  return http_response(
      status_code=200,
      body={
          "message": "Album updated successfully",
          "albumId": album_id,
          "presignedCoverUrl": presigned_cover_url,
      }
  )


def get_existing_album(album_id):
    response = table.get_item(Key={"PK": "ALBUM#" + album_id, "SK": "METADATA"})
    return response.get("Item")

def update_album_metadata(album_id, body, existing_album):
    item = {
        "PK": "ALBUM#" + album_id,
        "SK": "METADATA",
        "type": "album",
        "title": body.get("title", existing_album.get("title")),
        "artists": body.get("artists", existing_album.get("artists")),
        "genres": body.get("genres", existing_album.get("genres")),
        "year": body.get("year", existing_album.get("year")),
        "coverPath": body.get("coverPath", existing_album.get("coverPath")),
        "coverType": body.get("coverType", existing_album.get("coverType")),
        "description": body["description"],
        "totalTracks": existing_album.get("totalTracks", 0),
        "createdAt": existing_album.get("createdAt"),
        "updatedAt": datetime.utcnow().isoformat() + "Z",
    }
    table.put_item(Item=item)
    logger.info("Album metadata updated", extra={"album_id": album_id})


def sync_genre_relations(album: dict, body: dict, old_genres: set, new_genres: set) -> None:
    genres_to_add = new_genres - old_genres
    genres_to_remove = old_genres - new_genres
    genres_to_update = new_genres & old_genres

    title_changed = body["title"] != album.get("title")
    logger.info("album title changed from: %s, to %s", body["title"], album.get("title"))

    with genre_relations_table.batch_writer() as batch:
        for genre in genres_to_remove:
            batch.delete_item(Key={"PK": genre, "SK": album['PK']})


    add_genres(genres_to_add, album, body)

    if title_changed:
        update_genres(genres_to_update, album, body)



def add_genres(genres, album, body):
    with genre_relations_table.batch_writer() as batch:
        for genre in genres:
            batch.put_item(
                Item={
                    "PK": genre,
                    "SK": album['PK'].split('#')[1],
                    "Title": body["title"],
                    "CoverPath": body.get("coverPath", album.get("coverPath")),
                    "EntityType": "album"
                }
            )

def update_genres(genres, album, body):
    for genre in genres:
        genre_relations_table.update_item(
            Key={"PK": genre, "SK": album['PK'].split('#')[1]},
            UpdateExpression="SET #T = :title",
            ExpressionAttributeNames={"#T": "Title"},
            ExpressionAttributeValues={
                ":title": body["title"],
            },
        )


def sync_artist_relations_table(album, body):
    title_changed = body["title"] != album.get("title")
    if not title_changed: return

    artists_table=dynamodb.Table(os.environ['ARTIST_TABLE'])
    with artists_table.batch_writer() as batch:
        for artist in body['artists']:
            batch.put_item(
                Item={
                    "PK": artist,
                    "SK": album['PK'],
                    "EntityType": "album",
                    "Title": body['title'],
                }
            )