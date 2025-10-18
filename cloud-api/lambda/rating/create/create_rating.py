import json
import os
from datetime import datetime

import boto3
from util.exception_handler import handle_lambda_exceptions
from util.auth import require_role
from util.logger import logger
from util.http_response import http_response

from model.rating_request import RatingRequest

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['RATINGS_TABLE'])

@handle_lambda_exceptions
@require_role("admin", "user")
def handler(event, context):
    body = json.loads(event['body'])
    request = RatingRequest.model_validate(body)

    claims = event["requestContext"]["authorizer"]["claims"]
    user_id = claims["sub"]
    username = claims.get("cognito:username")

    rating = {
        "PK": request.content_id,
        "SK": f"USER#{user_id}",
        "rater": username,
        "type": request.content_type,
        "rating": request.rating,
        "createdAt": datetime.utcnow().isoformat()
    }

    if request.artistIds:
        rating['artistIds'] = request.artistIds
    if request.genres:
        rating['genres'] = request.genres

    table.put_item(Item=rating)

    return http_response(201, {"message": "Success!"})

