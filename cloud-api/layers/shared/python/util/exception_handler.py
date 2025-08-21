from botocore.exceptions import ClientError
from pydantic import ValidationError

from .http_response import http_response
from .logger import logger

COGNITO_ERROR_MAP = {
    "UsernameExistsException": (409, "Username already exists"),
    "InvalidPasswordException": (400, "Password does not meet requirements"),
    "InvalidParameterException": (400, "Invalid parameter(s)"),
    "UserNotConfirmedException": (403, "User not confirmed"),
    "UserNotFoundException": (404, "User not found"),
    "NotAuthorizedException": (401, "Unauthorized access"),
    "CodeMismatchException": (400, "Invalid confirmation code"),
    "ExpiredCodeException": (400, "Confirmation code expired"),
    "AliasExistsException": (409, "Alias already in use"),
    "MFAMethodNotFoundException": (400, "MFA method not found"),
    "TooManyRequestsException": (429, "Too many requests"),
    "LimitExceededException": (429, "Service limit exceeded"),
    "ResourceNotFoundException": (404, "Resource not found"),
    "UserLambdaValidationException": (400, "User validation failed"),
    "InvalidLambdaResponseException": (400, "Invalid Lambda response"),
    "UnexpectedLambdaException": (502, "Lambda function error"),
    "InternalErrorException": (500, "Internal Cognito error"),
    "InvalidSmsRoleAccessPolicyException": (400, "Invalid SMS role policy"),
}

def handle_lambda_exceptions(func):
    def wrapper(event, context):
        try:
            return func(event, context)

        except ValidationError as ve:
            logger.warning("Validation error", extra={"errors": ve.errors()})
            return http_response(400, {"error": ve.errors()})
        except ClientError as ce:
            error_code = ce.response['Error']['Code']
            status, message = COGNITO_ERROR_MAP.get(
                error_code, (502, "AWS service failure")
            )
            logger.warning(f"AWS ClientError: {error_code}", extra={"error": str(ce)})
            return http_response(status, {"error": message})
        except Exception as e:
            logger.exception("Unexpected error", extra={"error": str(e)})
            return http_response(500, {"error": "Internal server error"})

    return wrapper