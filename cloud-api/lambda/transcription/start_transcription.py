import boto3
import os
from util.logger import logger

MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
transcribe = boto3.client("transcribe")

def handler(event, context):

    for record in event["Records"]:
        key = record["s3"]["object"]["key"]
        
        if not key.lower().startswith("songs/"):
            continue

        job_name = key.replace("/", "_").replace(".", "_")
        file_uri = f"s3://{MEDIA_BUCKET}/{key}"

        try:
            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={"MediaFileUri": file_uri},
                LanguageCode="en-US",
                OutputBucketName=MEDIA_BUCKET,
                OutputKey=f"transcriptions/{os.path.basename(key)}.json"
            )
            logger.info(f"Started transcription for {key}")
        except transcribe.exceptions.ConflictException:
            logger.info(f"Job already exists for {key}, skipping...")