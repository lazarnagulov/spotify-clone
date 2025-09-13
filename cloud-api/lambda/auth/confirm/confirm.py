import os
import json
import boto3

from model.user_confirmation_request import UserConfirmationRequest
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.logger import logger

COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_REGION = os.environ.get("COGNITO_REGION")

client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

def confirm_sign_up(request: UserConfirmationRequest):
    return client.confirm_sign_up(
        ClientId=COGNITO_CLIENT_ID,
        Username=request.username,
        ConfirmationCode=request.code
    )

@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get('body', '{}'))
    request = UserConfirmationRequest.model_validate(body)

    response = confirm_sign_up(request)
    logger.info(f"Successfully confirmed registration for user {request.username}")
    return http_response(200, {"message": "User confirmed", "data": response})