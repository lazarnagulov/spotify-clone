import boto3
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.logger import logger

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
artists_table = dynamodb.Table('Artists')


@handle_lambda_exceptions
def handler(event, _context):
    response = artists_table.scan(ProjectionExpression="PK, SK")
    logger.info("Artists found", extra={'artist_count': len(response.get('Items', []))})

    artists = [
        {"id": item["PK"], "name": item["SK"]}
        for item in response.get("Items", [])
    ]

    return http_response(200, {'artists': artists})
