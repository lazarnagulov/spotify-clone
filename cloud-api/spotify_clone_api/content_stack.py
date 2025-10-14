from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_iam as iam,
    CfnOutput
)
from constructs import Construct


class ContentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, shared_layer_arn, api, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        shared_layer = aws_lambda.LayerVersion.from_layer_version_arn(self, "ImportedSharedLayer", shared_layer_arn)

        cors_rule = s3.CorsRule(
            allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.HEAD],
            allowed_origins=["*"],
            allowed_headers=["*"],
            exposed_headers=["ETag"],
            max_age=3600,
        )

        images_bucket = s3.Bucket(
            self, "ImagesBucket",
            bucket_name="cc-spotify-clone-images-bucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
            cors=[cors_rule],
        )

        audio_bucket = s3.Bucket(
            self,
            "SongsBucket",
            bucket_name="cc-spotify-clone-songs-bucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
            cors=[cors_rule]
        )

        generate_presigned_url_lambda = aws_lambda.Function(
            self, "GeneratePresignedUrlsFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="generate_presign_url.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/presigned_url"),
            layers=[shared_layer],
            environment={
                "AUDIO_BUCKET": audio_bucket.bucket_name,
                "IMAGE_BUCKET": images_bucket.bucket_name
            }
        )

        create_song_lambda = aws_lambda.Function(
            self, "CreateSongFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="create_song.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/song/create_song"),
            layers=[shared_layer],
            environment={
                "AUDIO_BUCKET": audio_bucket.bucket_name,
                "IMAGE_BUCKET": images_bucket.bucket_name,
                "SONGS_TABLE": "MusicCatalog",
            }
        )

        audio_bucket.grant_put(generate_presigned_url_lambda)
        images_bucket.grant_put(generate_presigned_url_lambda)

        audio_bucket.grant_put(create_song_lambda)
        images_bucket.grant_put(create_song_lambda)

        audio_bucket.grant_read(create_song_lambda)
        images_bucket.grant_read(create_song_lambda)

        create_song_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*"]
        ))

        upload_url = api.root.add_resource("upload-url")
        upload_url.add_method("POST", apigw.LambdaIntegration(generate_presigned_url_lambda))

        song_api = api.root.add_resource("songs")
        song_api.add_method("POST", apigw.LambdaIntegration(create_song_lambda))

        CfnOutput(self, "AudioBucketName", value=audio_bucket.bucket_name)
        CfnOutput(self, "ImagesBucketName", value=images_bucket.bucket_name)