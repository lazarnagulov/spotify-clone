import json, os, boto3
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.auth import require_role
from model.subscription_request import SubscriptionRequest

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['SUBSCRIPTION_TABLE'])


@handle_lambda_exceptions
@require_role("user", "admin")
def handler(event, context):
    body = json.loads(event['body'])
    request = SubscriptionRequest.model_validate(body)

    claims = event["requestContext"]["authorizer"]["claims"]
    user_id = claims["sub"]
    email = claims.get("email")
    username = claims.get("cognito:username")

    subscription = {
        'PK': user_id,
        'SK': request.content_id,
        'type': request.content_type,
        'email': email,
        'username': username
    }

    table.put_item(Item=subscription)

    return http_response(201, {"message": "Subscription success!"})
