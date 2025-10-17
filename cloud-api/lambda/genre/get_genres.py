import boto3
import json
import os

from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["GENRES_TABLE"])

@handle_lambda_exceptions
def handler(event, context):
    response = table.scan()
    items = response.get('Items', [])
    genres = [item["SK"] for item in items]
    return http_response(200, {'genres': genres})