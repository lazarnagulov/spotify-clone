import os
import json
import boto3

from model.register_request import RegisterRequest
from util.http_response import http_response
from util.logger import logger
from util.exception_handler import handle_lambda_exceptions

COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_REGION = os.environ.get("COGNITO_REGION")
COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID")

client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

def sign_up_user(request: RegisterRequest):
    return client.sign_up(
        ClientId=COGNITO_CLIENT_ID,
        Username=request.username,
        Password=request.password,
        UserAttributes=[
            {"Name": "email", "Value": request.email},
            {"Name": "name", "Value": request.name},
            {"Name": "family_name", "Value": request.family_name},
            {"Name": "birthdate", "Value": request.birthdate},
        ]
    )

def user_exists(email: str) -> bool:
    response = client.list_users(
        UserPoolId=COGNITO_USER_POOL_ID,
        Filter=f'email = "{email}"'
    )
    return len(response['Users']) > 0

@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get('body', '{}'))
    request = RegisterRequest.model_validate(body)

    if user_exists(request.email):
        return http_response(400, {"error": "User with this email already exists"})

    response = sign_up_user(request)

    logger.info(f"Successfully registered user {request.username} with email {request.email}")
    return http_response(201, {
        "message": "User registered successfully",
        "data": response.get("UserSub")
    })
