import json
import os
import boto3
from util.logger import logger

transcribe = boto3.client("transcribe")


def handler(event, context):
  for record in event["Records"]:
    body = json.loads(record["body"])
    bucket = body["bucket"]
    key = body["key"]

    job_name = key.replace("/", "_").replace(".", "_")
    file_uri = f"s3://{bucket}/{key}"
    output_key = f"transcriptions/{os.path.basename(key)}.json"

    try:
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": file_uri},
            LanguageCode="en-US",
            OutputBucketName=bucket,
            OutputKey=output_key
        )
    except transcribe.exceptions.ConflictException:
        logger.info(f"Job already exists for {key}, skipping...")
