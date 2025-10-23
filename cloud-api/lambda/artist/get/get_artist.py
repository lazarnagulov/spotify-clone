import boto3
from boto3.dynamodb.conditions import Key
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.logger import logger

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
artists_table = dynamodb.Table('Artists')

@handle_lambda_exceptions
def handler(event, _context):
    artist_id = event['pathParameters']['id']

    response = artists_table.query(
        KeyConditionExpression=Key('PK').eq(artist_id) & Key('SK').eq('METADATA'),
        ExpressionAttributeNames={
            '#n': 'name',
            '#b': 'bio',
            '#g': 'genres'
        },
        ProjectionExpression='#n, #b, #g'
    )

    items = response.get("Items", [])
    if not items:
        logger.info(f"Artist with id {artist_id} not found")
        return http_response(404, {"message": "Artist not found"})

    artist = items[0]

    logger.info(f"Artist with id {artist_id} found")
    return http_response(200, {
        "id": artist_id,
        "name": artist['name'],
        "bio": artist['bio'],
        "genres": artist['genres']
    })
