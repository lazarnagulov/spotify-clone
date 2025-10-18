import boto3, os
from boto3.dynamodb.conditions import Key

from util.exception_handler import handle_lambda_exceptions
from util.auth import require_role
from http_response import http_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['RATINGS_TABLE'])
music_table = dynamodb.Table(os.environ['MUSIC_TABLE'])

@handle_lambda_exceptions
@require_role("user", "admin")
def handler(event, context):
    content_id = event['pathParameters']['id']
    response = table.query(KeyConditionExpression=Key('PK').eq(content_id))

    ratings = response.get('Items', [])
    return http_response(200, ratings)

