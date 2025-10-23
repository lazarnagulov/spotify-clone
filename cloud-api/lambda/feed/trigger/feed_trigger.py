import json
import boto3
import os
from util.exception_handler import handle_lambda_exceptions
from util.logger import logger

dynamodb = boto3.resource("dynamodb")
sqs = boto3.client("sqs")

SQS_QUEUE_URL = os.environ["FEED_SQS_URL"]
USER_TABLES = ["Ratings", "ListeningHistory", "Subscriptions"]
GLOBAL_TABLES = ["MusicCatalog"]


@handle_lambda_exceptions
def handler(event, _context):
    logger.info("Feed trigger invoked.")

    for record in event.get('Records', []):
        event_name = record.get('eventName')
        logger.info(f"Event name: {event_name}")

        if event_name not in ['INSERT', 'MODIFY']:
            continue

        new_image = record.get('dynamodb', {}).get('NewImage', {})
        logger.info(f"New image: {new_image}")
        if not new_image:
            continue

        pk_value = new_image.get('PK', {}).get('S', '')
        if pk_value.startswith('ALBUM#'):
            continue

        table_name = record.get('eventSourceARN', '').split('/')[1]
        logger.info(f"Table name: {table_name}")

        if table_name in USER_TABLES: # User rated, subscribed, or listened -> send message for that user only
            user_id = new_image.get('PK', {}).get('S')
            if not user_id:
                continue
            user_ids = [user_id]
            logger.info(f"Preparing SQS message for user {user_id}")

        elif table_name in GLOBAL_TABLES: # Global action -> new content added by admin
            # TODO: filter users who are subscribed to the genre/artist
            user_ids = ['33648832-d091-70c7-083c-72209ba63d91']  # placeholder
            logger.info("Preparing SQS messages for all users")

        else:
            continue

        logger.info("Sending messages to SQS...")
        for user_id in user_ids:
            sqs.send_message(
                QueueUrl=SQS_QUEUE_URL,
                MessageBody=json.dumps({"userId": user_id})
            )
        logger.info("Messages successfully sent to SQS.")

    return {"message": "Success"}
