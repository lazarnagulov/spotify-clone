import os

import boto3

from util.http_response import http_response
from util.logger import logger

COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_REGION = os.environ.get("COGNITO_REGION")

client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

def extract_refresh_token(headers):
    cookie_header = headers.get("cookie", "")
    for cookie in cookie_header.split(";"):
        if cookie.strip().startswith("refreshToken="):
            return cookie.split("=")[1]
    return None

def handler(event, _context):
    headers = event.get("headers", {})
    refresh_token = extract_refresh_token(headers)
    if not refresh_token:
        return http_response(401, {"message": "No refresh token found"})

    response = client.initiate_auth(
        ClientId=COGNITO_CLIENT_ID,
        AuthFlow="REFRESH_TOKEN_AUTH",
        AuthParameters={"REFRESH_TOKEN": refresh_token}
    )

    return http_response(200, response["AuthenticationResult"])
