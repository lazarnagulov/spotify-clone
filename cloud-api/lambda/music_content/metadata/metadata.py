import os
from datetime import datetime

import boto3
from mutagen.mp3 import MP3

from logger import logger

dynamodb = boto3.client("dynamodb")
s3 = boto3.client("s3")
TABLE_NAME = os.environ["TABLE_NAME"]

def handler(event, _context):
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        tmp_path = f"/tmp/{os.path.basename(key)}"
        s3.download_file(bucket, key, tmp_path)

        audio = MP3(tmp_path)
        duration = int(audio.info.length)
        size = os.path.getsize(tmp_path)

        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                "track_id": {"S": key.split("/")[-1].split(".")[0]},
                "filename": {"S": key},
                "file_size": {"N": str(size)},
                "duration": {"N": str(duration)},
                "created_at": {"S": datetime.utcnow().isoformat()},
            }
        )

        logger.info("Metadata saved", extra={"file": key, "duration": duration})