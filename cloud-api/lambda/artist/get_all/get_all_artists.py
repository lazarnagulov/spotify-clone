import boto3
from boto3.dynamodb.conditions import Key, Attr
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.logger import logger

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
artists_table = dynamodb.Table('Artists')

@handle_lambda_exceptions
def handler(event, _context):
    response = artists_table.scan(
        FilterExpression=Attr("SK").eq("METADATA"),
        ExpressionAttributeNames={
            "#n": "name",
            "#p": "PK"
        },
        ProjectionExpression="#p, #n"
    )

    items = response.get("Items", [])
    logger.info("Artists found", extra={'artist_count': len(items)})

    artists = [
        {"id": item["PK"], "name": item["name"]}
        for item in items
    ]

    return http_response(200, {'artists': artists})
