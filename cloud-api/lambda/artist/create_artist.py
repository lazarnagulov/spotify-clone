import boto3
import json
import uuid
from model.create_artist_request import CreateArtistRequest
from util.exception_handler import handle_lambda_exceptions

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
artists_table = dynamodb.Table('Artists')

@handle_lambda_exceptions
def handler(event, context):
    body = json.loads(event.get("body", "{}"))
    request = CreateArtistRequest.model_validate(body)

    artist_id = str(uuid.uuid4())

    artists_table.put_item(
        Item={
            "PK": str(uuid.uuid4()),
            "SK": request.name,
            "bio": request.bio,
            "genres": request.genres
        }
    )

    return {
        'statusCode': 201,
        'body': json.dumps({'message': 'Artist created successfully'})
    }
