import boto3
import json
import uuid
from model.create_artist_request import CreateArtistRequest
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
artists_table = dynamodb.Table('Artists')
music_catalog_table = dynamodb.Table('MusicCatalog')

@handle_lambda_exceptions
def handler(event, context):
    body = json.loads(event.get("body", "{}"))
    request = CreateArtistRequest.model_validate(body)

    artist_id = str(uuid.uuid4())

    artists_table.put_item(
        Item={
            "PK": artist_id,
            "SK": request.name,
            "bio": request.bio,
            "genres": request.genres
        }
    )

    with music_catalog_table.batch_writer() as batch:
        for genre in request.genres:
            batch.put_item(
                Item={
                    "PK": f"GENRE#{genre}",
                    "SK": f"ARTIST#{artist_id}",
                    "name": request.name
                }
            )

    return http_response(201, {'message': 'Artist created successfully'})
