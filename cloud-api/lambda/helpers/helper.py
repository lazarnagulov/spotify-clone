import os
import boto3
from layers.shared.python.util import logger

s3_client = boto3.client("s3")
BUCKET_NAME = os.environ.get("BUCKET_NAME")

def generate_presigned_url(filename: str, expires_in: int = 3600) -> str:
  
  """
    Generates a presigned URL for uploading a file to S3.

    :param filename: the path/key in S3 (e.g., albums/album123/song1.mp3)
    :param expires_in: how many seconds the URL is valid for (default 1h)
    :return: presigned URL for upload
  """

  try:
    url = s3_client.generate_presigned_url(
      ClientMethod="put_object",
      Params={
        "Bucket": BUCKET_NAME,
        "Key": filename
      },
      ExpiresIn=expires_in
    )
    logger.info(f"Generated presigned URL for {filename}")
    return url
  except Exception as e:
    logger.error(f"Error generating presigned URL for {filename}: {e}", exc_info=True)
    raise
