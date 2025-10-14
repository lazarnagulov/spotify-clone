import os
import json
import uuid
import boto3
from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions
from util.logger import logger


s3 = boto3.client("s3")

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGE_BUCKET = os.environ["IMAGE_BUCKET"]

@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))
    file_type = body.get("file_type")
    content_type = body.get("content_type")

    if not file_type or not content_type:
        logger.warning("Missing required fields in request body")
        return http_response(400, {"error": "Missing file_type or content_type"})

    if file_type not in ("audio", "image"):
        logger.warning(f"Invalid file_type: {file_type}")
        return http_response(400, {"error": "Invalid file_type"})

    bucket = AUDIO_BUCKET if file_type == "audio" else IMAGE_BUCKET
    file_id = str(uuid.uuid4())
    file_key = f"{file_type}/{file_id}"

    presigned_url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket, "Key": file_key, "ContentType": content_type},
        ExpiresIn=300
    )

    logger.info("Presigned URL generated successfully", extra={"file_key": file_key})
    return http_response(200, {
        "upload_url": presigned_url,
        "file_key": file_key,
        "bucket": bucket,
        "expires_in": 300
    })
