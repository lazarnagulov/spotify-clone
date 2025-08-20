import os
import json
import boto3

from util.http_response import http_response
from util.logger import logger
from util.exception_handler import handle_lambda_exceptions

COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_REGION = os.environ.get("COGNITO_REGION")

client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get('body', '{}'))
    username = body['username']
    email = body['email']
    password = body['password']
    name = body['name']
    family_name = body['family_name']
    birthdate = body['birthdate']

    response = client.sign_up(
        ClientId=COGNITO_CLIENT_ID,
        Username=username,
        Password=password,
        UserAttributes=[
            {"Name": "email", "Value": email},
            {"Name": "name", "Value": name},
            {"Name": "family_name", "Value": family_name},
            {"Name": "birthdate", "Value": birthdate},
        ]
    )

    logger.info(f"Successfully registered user {username} with email {email}")
    return http_response(201, {
        "message": "User registered successfully",
        "data": response.get("UserSub")
    })
