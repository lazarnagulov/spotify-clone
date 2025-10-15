import json
from botocore.exceptions import ClientError
from pydantic import ValidationError

from .http_response import http_response
from .logger import logger

COGNITO_ERROR_MAP = {
    "UsernameExistsException": (409, "An account with this email already exists."),
    "InvalidPasswordException": (400, "Your password doesn't meet the security requirements."),
    "InvalidParameterException": (400, "Some information you provided is invalid. Please check and try again."),
    "UserNotConfirmedException": (403, "Your account hasn't been confirmed yet. Please check your email for the confirmation link."),
    "UserNotFoundException": (404, "We couldn’t find an account with that information."),
    "NotAuthorizedException": (401, "Incorrect username or password. Please try again."),
    "CodeMismatchException": (400, "The confirmation code you entered is incorrect."),
    "ExpiredCodeException": (400, "The confirmation code has expired. Please request a new one."),
    "AliasExistsException": (409, "This contact information is already linked to another account."),
    "MFAMethodNotFoundException": (400, "Multi-factor authentication method not found."),
    "TooManyRequestsException": (429, "You’ve made too many requests. Please wait a moment and try again."),
    "LimitExceededException": (429, "You’ve reached the maximum number of allowed requests. Try again later."),
    "ResourceNotFoundException": (404, "Requested resource not found."),
    "UserLambdaValidationException": (400, "There was a problem validating your account. Please contact support."),
    "InvalidLambdaResponseException": (400, "Something went wrong while processing your request. Please try again."),
    "UnexpectedLambdaException": (502, "A system error occurred. Please try again later."),
    "InternalErrorException": (500, "An internal error occurred. Please try again later."),
    "InvalidSmsRoleAccessPolicyException": (400, "There was a problem sending the SMS. Please contact support."),
}

def handle_lambda_exceptions(func):
    def wrapper(event, context):
        try:
            return func(event, context)

        except ValidationError as ve:
            logger.warning("Validation error", extra={"errors": ve.errors()})
            return http_response(400, {"error": json.loads(ve.json())})
        except PermissionError as pe:
            logger.warning("Permission denied", extra={"error": str(pe)})
            return http_response(403, {"error": "Forbidden"})
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