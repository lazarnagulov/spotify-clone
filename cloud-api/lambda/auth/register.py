from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions
from util.logger import logger

@handle_lambda_exceptions
def handler(event, context):
    logger.info("Logged from register lambda")
    print("Hello world")
    return http_response(200, "")