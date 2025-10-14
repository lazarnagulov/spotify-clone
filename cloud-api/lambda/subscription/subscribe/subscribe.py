from util.exception_handler import handle_lambda_exceptions


@handle_lambda_exceptions
def handler(event, context):
    ...