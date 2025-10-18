import os
import boto3
import json
from boto3.dynamodb.conditions import Key
from util.logger import logger
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response

dynamodb = boto3.resource("dynamodb", region_name="eu-central-1")

subscription_table = dynamodb.Table(os.environ["SUBSCRIPTION_TABLE"])
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genres_table = dynamodb.Table(os.environ["GENRES_TABLE"])


def get_user_id(event):
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    return claims.get("sub") or claims.get("user_id")

@handle_lambda_exceptions
def handler(event, _context):
    user_id = get_user_id(event)
    logger.info(f"Fetching subscriptions for user: {user_id}")

    response = subscription_table.query(
        KeyConditionExpression=Key("PK").eq(user_id)
    )

    items = response.get("Items", [])
    results = []

    for item in items:
        content_id = item["SK"]
        sub_type = item["type"]

        display = {
            "contentId": content_id,
            "type": sub_type,
        }

        if sub_type == "artist":
            try:
                artist = artists_table.get_item(
                    Key={"PK": content_id, "SK": "METADATA"}
                ).get("Item")
                if artist:
                    display["name"] = artist.get("name")
            except Exception as e:
                logger.error(f"Error fetching artist {content_id}: {e}")

        elif sub_type == "genre":
            try:
                genre = genres_table.get_item(
                    Key={"PK": "GENRE", "SK": content_id}
                ).get("Item")
                if genre:
                    display["name"] = genre["SK"]
            except Exception as e:
                logger.error(f"Error fetching genre {content_id}: {e}")

        results.append(display)

    return http_response(200, results)
