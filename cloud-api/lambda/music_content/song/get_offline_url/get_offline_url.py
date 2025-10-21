import os
import boto3
from util.auth import require_role
from util.exception_handler import handle_lambda_exceptions
from util.http_response import http_response
from util.logger import logger

s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")
MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
AWS_REGION = "eu-central-1"

@handle_lambda_exceptions
@require_role("user", "admin")
def handler(event, context):
    song_id = event["pathParameters"]["id"]
    if not song_id.startswith("SONG#"):
        song_id = f"SONG#{song_id}"

    response = dynamodb.get_item(
        TableName=os.environ["SONGS_TABLE"],
        Key={"PK": {"S": song_id}, "SK": {"S": "METADATA"}}
    )

    if "Item" not in response:
        return http_response(404, {"error": "Song not found"})

    song = response["Item"]
    audio_path = song.get("audioPath", {}).get("S")
    if not audio_path:
        return http_response(400, {"error": "Missing audio path"})

    offline_url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': MEDIA_BUCKET,
            'Key': audio_path,
            'ResponseContentType': 'audio/mpeg'
        },
        ExpiresIn=3600
    )

    logger.info(f"Returning offline URL for {song_id}: {offline_url}")

    return http_response(200, {"offline_url": offline_url})
