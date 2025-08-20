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
    body = json.loads(event.get('body', "{}"))
    username = body['username']
    password = body['password']

    response = client.initiate_auth(
        ClientId=COGNITO_CLIENT_ID,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        }
    )
    logger.info(f"{username} has been logged successfully.")
    return http_response(200, response['AuthenticationResult'])
