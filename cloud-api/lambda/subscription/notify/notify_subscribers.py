import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer
from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions

dynamodb_resource = boto3.resource("dynamodb")
dynamodb_client = boto3.client("dynamodb")
sns = boto3.client("sns")

TABLE_NAME = os.environ["SUBSCRIPTION_TABLE"]
TOPIC_ARN = os.environ["NOTIFICATIONS_TOPIC_ARN"]
INDEX_NAME = os.environ.get("CONTENT_INDEX", "ContentIndex")
ARTISTS_TABLE = os.environ["ARTISTS_TABLE"]

subscription_table = dynamodb_resource.Table(TABLE_NAME)

deserializer = TypeDeserializer()


def deserialize_item(item):
    return {k: deserializer.deserialize(v) for k, v in item.items()}

def get_artist_names(artist_ids):
    if not artist_ids:
        return []

    request_items = {
        ARTISTS_TABLE: {
            "Keys": [{"PK": {"S": artist_id}, "SK": {"S": "METADATA"}} for artist_id in artist_ids],
            "ProjectionExpression": "PK, #n",
            "ExpressionAttributeNames": {"#n": "name"}
        }
    }

    response = dynamodb_client.batch_get_item(RequestItems=request_items)
    artists = response.get("Responses", {}).get(ARTISTS_TABLE, [])

    artist_name_map = {}
    for artist in artists:
        artist_data = deserialize_item(artist)
        artist_name_map[artist_data["PK"]] = artist_data.get("name", "Unknown")

    return [artist_name_map.get(artist_id, "Unknown") for artist_id in artist_ids]


@handle_lambda_exceptions
def handler(event, _context):
    artist_ids = event.get("artist_ids", [])
    event_type = event.get("event_type")
    genres = event.get("genres", [])

    artist_names = get_artist_names(artist_ids)

    all_subs = []
    for artist_id in artist_ids:
        artist_subs = subscription_table.query(
            IndexName=INDEX_NAME,
            KeyConditionExpression=Key("SK").eq(artist_id)
        ).get("Items", [])
        all_subs.extend(artist_subs)

    for genre in genres:
        resp = subscription_table.query(
            IndexName=INDEX_NAME,
            KeyConditionExpression=Key("SK").eq(genre)
        ).get("Items", [])
        all_subs.extend(resp)

    subscribers = {sub["email"]: sub for sub in all_subs}.values()

    if not subscribers:
        return http_response(200, {"message": "No subscribers to notify."})

    artists_display = format_artist_names(artist_names)

    if event_type == "song":
        message = f"New song '{event['song_title']}' by {artists_display} is now available!"
        subject = "New song released!"
    elif event_type == "album":
        songs = ", ".join(event.get("songs", []))
        message = f"New album '{event['album_title']}' by {artists_display} has been released!\nTracks: {songs}"
        subject = "New album released!"
    else:
        message = f"New content from {artists_display} is now available!"
        subject = "New content available"

    sns.publish(TopicArn=TOPIC_ARN, Subject=subject, Message=json.dumps({
        "subject": subject,
        "message": message,
        "emails": [sub["email"] for sub in subscribers]
    }))

    return http_response(200, {
        "message": f"Notified {len(list(subscribers))} users",
        "type": event_type,
        "artists": artist_names
    })


def format_artist_names(artist_names):
    if not artist_names:
        return "Unknown Artist"
    elif len(artist_names) == 1:
        return artist_names[0]
    elif len(artist_names) == 2:
        return f"{artist_names[0]} and {artist_names[1]}"
    else:
        return ", ".join(artist_names[:-1]) + f", and {artist_names[-1]}"