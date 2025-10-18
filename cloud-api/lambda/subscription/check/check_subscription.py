import os, json, boto3
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.auth import require_role

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['SUBSCRIPTION_TABLE'])


@handle_lambda_exceptions
@require_role("user", "admin")
def handler(event, context):
    params = event.get("queryStringParameters") or {}
    content_id = params.get("content_id")

    if not content_id:
        return http_response(400, {"message": "Missing required parameter: content_id"})

    claims = event["requestContext"]["authorizer"]["claims"]
    user_id = claims["sub"]

    response = table.get_item(Key={'PK': user_id, 'SK': content_id})

    is_subscribed = 'Item' in response

    return http_response(200, {"subscribed": is_subscribed})
