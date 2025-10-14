import os
from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda,
    aws_s3 as s3,
    CfnOutput
)
from constructs import Construct


class ContentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, shared_layer_arn, content_layer_arn, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        shared_layer = aws_lambda.LayerVersion.from_layer_version_arn(self, "ImportedSharedLayer", shared_layer_arn)
        content_layer = aws_lambda.LayerVersion.from_layer_version_arn(self, "ImportedContentLayer", content_layer_arn)

        cors_rule = s3.CorsRule(
            allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.HEAD],
            allowed_origins=["*"],
            allowed_headers=["*"],
            exposed_headers=["ETag"],
            max_age=3600,
        )

        images_bucket = s3.Bucket(
            self, "ImagesBucket",
            bucket_name=os.getenv("IMAGES_BUCKET"),
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            cors=[cors_rule],
        )

        audio_bucket = s3.Bucket(
            self, "AudioBucket",
            bucket_name=os.getenv("AUDIO_BUCKET"),
            versioned=True,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            cors=[cors_rule],
        )

        generate_presigned_url_lambda = aws_lambda.Function(
            self, "GeneratePresignedUrlsFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="generate_presign_url.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/presigned_url"),
            layers=[shared_layer, content_layer],
            environment={
                "AUDIO_BUCKET": audio_bucket.bucket_name,
                "IMAGE_BUCKET": images_bucket.bucket_name
            }
        )

        audio_bucket.grant_put(generate_presigned_url_lambda)
        images_bucket.grant_put(generate_presigned_url_lambda)

        # audio_bucket.add_event_notification(
        #     s3.EventType.OBJECT_CREATED,
        #     s3n.LambdaDestination(metadata_lambda)
        # )

        CfnOutput(self, "AudioBucketName", value=audio_bucket.bucket_name)
        CfnOutput(self, "ImagesBucketName", value=images_bucket.bucket_name)
