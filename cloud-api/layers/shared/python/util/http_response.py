import json
from typing import Union, Dict, List, Optional


def http_response(
        status_code: int,
        body: Union[Dict, str],
        headers: Optional[Dict]=None,
        cookies: Optional[List[str]]=None
):
    if not isinstance(body, str):
        body = json.dumps(body)

    response_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, HEAD",
        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Amz-Date, X-Api-Key, Accept"
    }

    if headers:
        response_headers.update(headers)

    response = {
        "statusCode": status_code,
        "headers": response_headers,
        "body": body
    }

    if cookies:
        response["multiValueHeaders"] = {"Set-Cookie": cookies}

    return response