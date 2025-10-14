import os
import json
import uuid
import boto3
from util.http_response import http_response
from util.exception_handler import handle_lambda_exceptions
from util.logger import logger

s3 = boto3.client("s3", region_name="eu-central-1")

AUDIO_BUCKET = os.environ["AUDIO_BUCKET"]
IMAGE_BUCKET = os.environ["IMAGE_BUCKET"]
EXPIRATION_TIME = int(os.environ.get("EXPIRATION_TIME", 300))


@handle_lambda_exceptions
def handler(event, _context):
    body = json.loads(event.get("body", "{}"))
    file_type = body.get("file_type")
    content_type = body.get("content_type", "application/octet-stream")
    file_name = body.get("file_name")  # optional: client can provide a name

    if not file_type or file_type not in ("audio", "image"):
        logger.warning(f"Invalid or missing file_type: {file_type}")
        return http_response(400, {"error": "Invalid or missing file_type"})

    bucket = AUDIO_BUCKET if file_type == "audio" else IMAGE_BUCKET

    extension = content_type.split("/")[-1]
    file_id = str(uuid.uuid4()) if not file_name else file_name
    file_key = f"{file_type}/{file_id}.{extension}"

    presigned_url = s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": bucket, "Key": file_key, "ContentType": content_type},
        ExpiresIn=EXPIRATION_TIME,
        HttpMethod="PUT"
    )

    logger.info("Presigned URL generated successfully", extra={"file_key": file_key})
    logger.info(f"Expected Content-Type for presigned URL: {content_type}")

    return http_response(200, {
        "upload_url": presigned_url,
        "file_key": file_key,
        "bucket": bucket,
        "expires_in": EXPIRATION_TIME
    })
