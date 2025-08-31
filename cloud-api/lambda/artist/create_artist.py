import boto3
import json
import uuid
from util.exception_handler import handle_lambda_exceptions
from model.create_artist_request import CreateArtistRequest

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table = dynamodb.Table('MusicCatalog')

@handle_lambda_exceptions
def handler(event, context):
    body = json.loads(event.get("body", "{}"))
    request = CreateArtistRequest.model_validate(body)

    with table.batch_writer() as batch:
        for genre in request.genres:
            batch.put_item(
                Item={
                    "PK": genre,
                    "SK": "ARTIST#" + str(uuid.uuid4()),
                    "name": request.name,
                    "bio": request.bio,
                }
            )
    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Artist created successfully'})
    }

