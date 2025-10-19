import json
import os
import boto3
from boto3.dynamodb.conditions import Key
from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

TABLE_NAME = os.environ["SUBSCRIPTION_TABLE"]
TOPIC_ARN = os.environ["NOTIFICATIONS_TOPIC_ARN"]
INDEX_NAME = os.environ.get("CONTENT_INDEX", "ContentIndex")

subscription_table = dynamodb.Table(TABLE_NAME)


@handle_lambda_exceptions
def handler(event, _context):
    artist_id = event.get("artist_id")
    artist_name = event.get("artist_name")
    event_type = event.get("event_type")
    genres = event.get("genres", [])

    artist_subs = subscription_table.query(
        IndexName=INDEX_NAME,
        KeyConditionExpression=Key("SK").eq(artist_id)
    ).get("Items", [])

    genre_subs = []
    for genre in genres:
        resp = subscription_table.query(
            IndexName=INDEX_NAME,
            KeyConditionExpression=Key("SK").eq(genre)
        ).get("Items", [])
        genre_subs.extend(resp)

    subscribers = {sub["email"]: sub for sub in artist_subs + genre_subs}.values()

    if not subscribers:
        return http_response(200, {"message": "No subscribers to notify."})

    if event_type == "song":
        message = f"New song '{event['song_title']}' by {artist_name} is now available!"
        subject = "New song released!"
    elif event_type == "album":
        songs = ", ".join(event.get("songs", []))
        message = f"New album '{event['album_title']}' by {artist_name} has been released!\nTracks: {songs}"
        subject = "New album released!"
    else:
        message = f"New content from {artist_name} is now available!"
        subject = "New content available"

    sns.publish(TopicArn=TOPIC_ARN, Subject=subject, Message=json.dumps({
        "subject": subject,
        "message": message,
        "emails": [sub["email"] for sub in subscribers]
    }))

    return http_response(200, {
        "message": f"Notified {len(list(subscribers))} users",
        "type": event_type
    })
