import boto3
import os
import json
from botocore.exceptions import ClientError

from util.auth import require_role
from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions
from util.logger import logger 

MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
s3 = boto3.client("s3")

def cors_response(status_code, body=None):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "GET,OPTIONS"
    }
    logger.info(f"[CORS_RESPONSE] status={status_code}, body={body}")
    return http_response(status_code, body, headers=headers)


@handle_lambda_exceptions
def handler(event, context):

    if event.get("httpMethod") == "OPTIONS":
        return cors_response(200)

    song_id = event.get("pathParameters", {}).get("id")

    if not song_id:
        return cors_response(400, {"error": "Missing song ID"})

    transcription_key = f"transcriptions/{song_id}.json"
    logger.info(f"[TRANSCRIPTION_KEY] Looking for key: {transcription_key} in bucket {MEDIA_BUCKET}")

    try:
        response = s3.get_object(Bucket=MEDIA_BUCKET, Key=transcription_key)
        logger.info("[S3_SUCCESS] Object fetched successfully.")
        content = response["Body"].read().decode("utf-8")
        data = json.loads(content)
        transcript = data.get("results", {}).get("transcripts", [{}])[0].get("transcript")
    except ClientError as e:
        logger.error(f"[S3_ERROR] {e}")
        if e.response["Error"]["Code"] == "NoSuchKey":
            transcript = None
        else:
            logger.exception("[UNEXPECTED_ERROR] Unexpected S3 error occurred.")
            return cors_response(500, {"error": "Unexpected error"})

    logger.info("[HANDLER_END] Returning transcript result.")
    return http_response(
        200,
        {"transcript": transcript},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,OPTIONS"
        }
    )
