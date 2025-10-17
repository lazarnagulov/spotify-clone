import os
import boto3
import json
import uuid
from model.create_artist_request import CreateArtistRequest
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.auth import require_role

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table(os.environ["MUSIC_CATALOG"])
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])

@handle_lambda_exceptions
@require_role('admin')
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))
    request = CreateArtistRequest.model_validate(body)

    artist_id = str(uuid.uuid4())

    artists_table.put_item(
        Item={
            "PK": artist_id,
            "SK": "METADATA",
            "name": request.name,
            "bio": request.bio,
            "genres": request.genres
        }
    )

    update_genre_relations_table(request, artist_id)

    return http_response(201, {'message': 'Artist created successfully'})


def update_genre_relations_table(request, artist_id):
    genre_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])

    for genre in request.genres:
        genre_table.put_item(
            Item={
                "PK": genre,
                "SK": artist_id,
                "EntityType": "artist",
                "Name": request.name
            }
        )