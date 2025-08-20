import os
import json
import boto3
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.logger import logger

COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_REGION = os.environ.get("COGNITO_REGION")

client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get('body', '{}'))
    username = body['username']
    code = body['code']

    response = client.confirm_sign_up(
        ClientId=COGNITO_CLIENT_ID,
        Username=username,
        ConfirmationCode=code
    )
    logger.info(f"Successfully confirmed registration for user {username}")
    return http_response(200, {"message": "User confirmed", "data": response})