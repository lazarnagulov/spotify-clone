import json, boto3, os
from boto3.dynamodb.conditions import Key

from http_response import http_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['ratingsTable'])


def handler(event, context):
    content_id = event['pathParameters']['contentId']
    resp = table.query(
        KeyConditionExpression=Key('PK').eq(content_id)
    )

    ratings = resp.get('Items', [])
    return http_response(200, ratings)
