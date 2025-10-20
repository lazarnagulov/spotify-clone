import boto3
import os
from util.logger import logger
from botocore.exceptions import ClientError

from util.exception_handler import handle_lambda_exceptions

MEDIA_BUCKET = os.environ["MEDIA_BUCKET"]
transcribe = boto3.client("transcribe")

@handle_lambda_exceptions
def handler(event, context):
    for record in event["Records"]:
        key = record["s3"]["object"]["key"]

        if not key.lower().startswith("songs/"):
            continue

        job_name = key.replace("/", "_").replace(".", "_")
        file_uri = f"s3://{MEDIA_BUCKET}/{key}"
        output_key = f"transcriptions/{os.path.basename(key)}.json"

        try:
            status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = status["TranscriptionJob"]["TranscriptionJobStatus"]

            if job_status == "COMPLETED":
                logger.info(f"Transcription already completed for {key}")
                continue
            elif job_status == "FAILED":
                logger.warning(f"Transcription failed for {key}, retrying...")
                transcribe.delete_transcription_job(TranscriptionJobName=job_name)

        except ClientError as e:
            if e.response["Error"]["Code"] == "BadRequestException" and \
               "couldn't be found" in e.response["Error"]["Message"]:
                logger.info(f"No existing transcription job found for {key}, creating new one")
            else:
                logger.error(f"Unexpected error checking job {job_name}: {e}")
                continue

        try:
            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={"MediaFileUri": file_uri},
                LanguageCode="en-US",
                OutputBucketName=MEDIA_BUCKET,
                OutputKey=output_key
            )
        except transcribe.exceptions.ConflictException:
            logger.info(f"Job already exists for {key}, skipping...")
