import json
import boto3
import os

from util.logger import logger
from util.exception_handler import handle_lambda_exceptions

ses = boto3.client('ses')

SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "no-reply@example.com")

@handle_lambda_exceptions
def handler(event, context):
    for record in event['Records']:
        sns_message = record['Sns']['Message']
        message_data = json.loads(sns_message)

        subject = message_data.get("subject", "New Content Available")
        body = message_data.get("message", "")
        emails = message_data.get("emails", [])

        if not emails:
            logger.warn("No emails to send.")
            continue

        for email in emails:
            send_email(email, subject, body)

        logger.info(f"Successfully sent emails to {len(emails)} recipients.")


def send_email(to_address, subject, body):
    response = ses.send_email(
        Source=SENDER_EMAIL,
        Destination={
            'ToAddresses': [to_address],
        },
        Message={
            'Subject': {
                'Data': subject,
            },
            'Body': {
                'Text': {
                    'Data': body,
                },
            }
        }
    )
    logger.info(f"Email sent to {to_address}, SES Message ID: {response['MessageId']}")
