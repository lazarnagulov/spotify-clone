import os
import boto3
from layers.shared.python.util import logger

s3_client = boto3.client("s3")
DEFAULT_BUCKET_NAME = os.environ.get("BUCKET_NAME")

def generate_presigned_url(
    filename: str,
    bucket_name: str = None,
    expires_in: int = 3600,
    content_type: str = None
) -> str:
    """
    Generates a presigned URL for uploading a file to S3.

    :param filename: the path/key in S3 (e.g., albums/album123/song1.mp3)
    :param bucket_name: S3 bucket name; if None, uses default from environment
    :param expires_in: how many seconds the URL is valid for (default 1h)
    :param content_type: optional MIME type of the file to upload
    :return: presigned URL for upload
    """

    if bucket_name is None:
        bucket_name = DEFAULT_BUCKET_NAME

    params = {
        "Bucket": bucket_name,
        "Key": filename
    }
    if content_type:
        params["ContentType"] = content_type

    try:
        url = s3_client.generate_presigned_url(
            ClientMethod="put_object",
            Params=params,
            ExpiresIn=expires_in
        )
        logger.info(f"Generated presigned URL for {filename} in bucket {bucket_name}")
        return url
    except Exception as e:
        logger.error(f"Error generating presigned URL for {filename}: {e}", exc_info=True)
        raise
