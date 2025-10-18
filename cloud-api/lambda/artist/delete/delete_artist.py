import boto3, os
from util.http_response import http_response

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
artists_table = dynamodb.Table(os.environ["ARTISTS_TABLE"])
genre_relations_table = dynamodb.Table(os.environ["GENRE_RELATIONS_TABLE"])

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

    artists_table.delete_item(
        Key={"PK": pk, "SK": "METADATA"}
    )

    with genre_relations_table.batch_writer() as batch:
        for genre in genres:
            genre_value = genre["S"] if isinstance(genre, dict) else genre
            batch.delete_item(
                Key={
                    "PK": genre_value,
                    "SK": pk
                }
            )

    return http_response(200, {"message": "Artist successfully deleted"})
