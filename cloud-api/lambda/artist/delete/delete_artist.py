import boto3, os
from boto3.dynamodb.conditions import Key
from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions
from util.auth import require_role
from util.logger import logger

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genre_relations_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])
subscription_table = dynamodb.Table(os.environ["SUBSCRIPTION_TABLE"])

@handle_lambda_exceptions
@require_role('admin')
def handler(event, _context):
    pk = event["pathParameters"]["id"]

    response = artists_table.get_item(
        Key={"PK": pk, "SK": "METADATA"}
    )

    if "Item" not in response:
        return http_response(404, {"message": "Artist not found"})

    artist_item = response["Item"]
    genres = artist_item.get("genres", [])

    artists_table.delete_item(Key={"PK": pk, "SK": "METADATA"})
    logger.info("Artist deleted successfully", extra={"artist_id": pk})

    delete_genre_relations(genres, pk)
    delete_subscriptions(pk)

    return http_response(200, {"message": "Artist successfully deleted"})

def delete_genre_relations(genres, pk):
    with genre_relations_table.batch_writer() as batch:
        for genre in genres:
            genre_value = genre["S"] if isinstance(genre, dict) else genre
            batch.delete_item(
                Key={
                    "PK": genre_value,
                    "SK": pk
                }
            )

def delete_subscriptions(pk):
    with subscription_table.batch_writer() as batch:
        response = subscription_table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("SK").eq(pk)
        )
        logger.info("Deleting", extra={"items": response["Items"]})

        for item in response['Items']:
            batch.delete_item(
                Key={
                    "PK": item["PK"],
                    "SK": item["SK"]
                }
            )
