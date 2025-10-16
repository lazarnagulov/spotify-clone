from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_iam as iam,
    CfnOutput, Duration
)
from constructs import Construct


class ContentStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, authorizer, shared_layer, api, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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

        create_song_lambda = aws_lambda.Function(
            self, "CreateSongFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="create_song.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/song/create_song"),
            layers=[shared_layer],
            environment={
                "MEDIA_BUCKET": images_bucket.bucket_name,
                "MUSIC_CATALOG": "MusicCatalog",
                "GENRE_RELATIONS_TABLE": "GenreRelationsTable"
            }
        )

        create_album_lambda = aws_lambda.Function(
            self, "CreateAlbumFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="create_album.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/album/create_album"),
            layers=[shared_layer],
            timeout=Duration.seconds(60),
            environment={
                "MEDIA_BUCKET": images_bucket.bucket_name,
                "MUSIC_CATALOG": "MusicCatalog",
                "GENRE_RELATIONS_TABLE": "GenreRelationsTable"
            }
        )

        audio_bucket.grant_put(create_song_lambda)
        images_bucket.grant_put(create_song_lambda)

        audio_bucket.grant_read(create_song_lambda)
        images_bucket.grant_read(create_song_lambda)

        audio_bucket.grant_put(create_album_lambda)
        images_bucket.grant_put(create_album_lambda)

        audio_bucket.grant_read(create_album_lambda)
        images_bucket.grant_read(create_album_lambda)


        create_song_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*", 
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelationsTable*"]
        ))

        create_album_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*",
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelationsTable*"]
        ))

        song_api = api.root.add_resource("songs")
        song_api.add_method("POST", apigw.LambdaIntegration(create_song_lambda), authorizer=authorizer)

        song_api = api.root.add_resource("albums")
        song_api.add_method("POST", apigw.LambdaIntegration(create_album_lambda), authorizer=authorizer)

        CfnOutput(self, "AudioBucketName", value=audio_bucket.bucket_name)
        CfnOutput(self, "ImagesBucketName", value=images_bucket.bucket_name)