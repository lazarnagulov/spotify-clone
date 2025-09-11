import json


def http_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            'Access-Control-Allow-Origin': '*' # TODO: change once frontend is deployed
        },
        "body": json.dumps(body)
    }