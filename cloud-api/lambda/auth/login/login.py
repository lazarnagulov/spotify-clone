import os
import json
import boto3

from model.login_request import LoginRequest
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.logger import logger

COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID")
COGNITO_REGION = os.environ.get("COGNITO_REGION")

client = boto3.client('cognito-idp', region_name=COGNITO_REGION)


def authenticate(request: LoginRequest):
    return client.initiate_auth(
        ClientId=COGNITO_CLIENT_ID,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': request.username,
            'PASSWORD': request.password
        }
    )

def get_cookies(auth_result):
    cookies = []
    if "RefreshToken" in auth_result:
        refresh_token = auth_result["RefreshToken"]
        cookie_str = f"refreshToken={refresh_token}; HttpOnly; Path=/; SameSite=None; Secure"
        cookies.append(cookie_str)

    return cookies

@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get('body', "{}"))
    request = LoginRequest.model_validate(body)

    response = authenticate(request)
    auth_result = response['AuthenticationResult']
    logger.info(f"{request.username} has been logged successfully.")
    cookies = get_cookies(auth_result)
    return http_response(200, auth_result, cookies=cookies)
