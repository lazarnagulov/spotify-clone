import json
from botocore.exceptions import ClientError
from pydantic import ValidationError

from util.http_response import http_response
from util.logger import logger


def handle_lambda_exceptions(func):
    def wrapper(event, context):
        try:
            return func(event, context)

        except ValidationError as ve:
            logger.warning("Validation error", extra={"errors": ve.errors()})
            return http_response(400, {"error": json.loads(ve.json())})
        except ClientError as ce:
            logger.error("AWS ClientError", extra={"error": str(ce)})
            return http_response(502, {"error": "AWS service failure"})
        except Exception as e:
            logger.exception("Unexpected error")
            return http_response(500, {"error": "Internal server error"})


    return wrapper