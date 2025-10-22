from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_lambda,
    aws_apigateway as apigw,
    aws_s3 as s3,
    aws_iam as iam,
    CfnOutput, Duration
)
from aws_cdk import aws_s3_notifications as s3n
from aws_cdk import aws_sqs as sqs
from aws_cdk import aws_lambda_event_sources as lambda_events
from constructs import Construct


class ContentStack(Stack):

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        authorizer,
        shared_layer,
        notify_subscribers_fn,
        api,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cors_rule = s3.CorsRule(
            allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.PUT, s3.HttpMethods.POST, s3.HttpMethods.HEAD],
            allowed_origins=["*"],
            allowed_headers=["*"],
            exposed_headers=["ETag"],
            max_age=3600,
        )

        self.images_bucket = s3.Bucket(
            self, "ImagesBucket",
            bucket_name="cc-spotify-clone-images-bucket",
            auto_delete_objects=True,
            removal_policy=RemovalPolicy.DESTROY,
            cors=[cors_rule],
            public_read_access=True,
            object_ownership=s3.ObjectOwnership.OBJECT_WRITER,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            )
        )

        self.images_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=["s3:GetObject"],
                resources=[f"{self.images_bucket.bucket_arn}/*"]
            )
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
            code=aws_lambda.Code.from_asset("lambda/music_content/song/create"),
            layers=[shared_layer],
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name,
                "MUSIC_CATALOG": "MusicCatalog",
                "GENRE_RELATIONS_TABLE": "GenreRelations",
                "NOTIFY_SUBSCRIBERS_FUNCTION": notify_subscribers_fn.function_name
            }
        )

        delete_song_lambda = aws_lambda.Function(
            self,
            "DeleteSongFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="delete_song.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/song/delete"),
            layers=[shared_layer],
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name,
                "MUSIC_CATALOG": "MusicCatalog",
                "GENRE_RELATIONS_TABLE": "GenreRelations"
            }
        )

        create_album_lambda = aws_lambda.Function(
            self, "CreateAlbumFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="create_album.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/album/create"),
            layers=[shared_layer],
            timeout=Duration.seconds(60),
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name,
                "MUSIC_CATALOG": "MusicCatalog",
                "GENRE_RELATIONS_TABLE": "GenreRelations",
                "NOTIFY_SUBSCRIBERS_FUNCTION": notify_subscribers_fn.function_name
            }
        )

        delete_album_lambda = aws_lambda.Function(
            self, 
            "DeleteAlbumFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="delete_album.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/album/delete"),
            layers=[shared_layer],
            timeout=Duration.seconds(60),
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name,
                "MUSIC_CATALOG": "MusicCatalog",
                "GENRE_RELATIONS_TABLE": "GenreRelations"
            }
        )

        get_song_lambda = aws_lambda.Function(
            self, "GetSongFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_song.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/song/get"),
            layers=[shared_layer],
            timeout=Duration.seconds(15),
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name,
                "SONGS_TABLE": "MusicCatalog",
                'ARTISTS_TABLE': "Artists",
            }
        )

        get_transcription_lambda = aws_lambda.Function(
            self, "GetTranscriptionFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_transcription.handler",
            code=aws_lambda.Code.from_asset("lambda/transcription/get"),
            layers=[shared_layer],
            timeout=Duration.seconds(15),
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name
            }
        )

        get_album_lambda = aws_lambda.Function(
            self, "GetAlbumFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_album.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/album/get"),
            layers=[shared_layer],
            timeout=Duration.seconds(15),
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name,
                "SONGS_TABLE": "MusicCatalog",
                'ARTISTS_TABLE': "Artists",
            }
        )

        get_discover_page = aws_lambda.Function(
            self, "GetDiscoverPageFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_discover_page.handler",
            code=aws_lambda.Code.from_asset("lambda/music_content/discover_page"),
            layers=[shared_layer],
            timeout=Duration.seconds(15),
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name,
                "SONGS_TABLE": "MusicCatalog",
                "GENRE_RELATIONS_TABLE": "GenreRelations"
            }
        )

        audio_bucket.grant_put(create_song_lambda)
        self.images_bucket.grant_put(create_song_lambda)

        audio_bucket.grant_read(create_song_lambda)
        self.images_bucket.grant_read(create_song_lambda)

        audio_bucket.grant_put(create_album_lambda)
        self.images_bucket.grant_put(create_album_lambda)

        audio_bucket.grant_read(create_album_lambda)
        self.images_bucket.grant_read(create_album_lambda)



        create_song_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "lambda:InvokeFunction"
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*", 
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelations*",
                       notify_subscribers_fn.function_arn ]
        ))

        delete_song_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:BatchWriteItem",
                    "s3:DeleteObject"
                ],
                resources=[
                    f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*",
                    f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelations*",
                    "arn:aws:s3:::cc-spotify-clone-images-bucket/songs/*",
                    "arn:aws:s3:::cc-spotify-clone-images-bucket/covers/*"
                ]
            )
        )

        create_album_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "lambda:InvokeFunction"
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*",
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelations*",
                       notify_subscribers_fn.function_arn]
        ))

        delete_album_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:Query",
                "dynamodb:GetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:DeleteItem",
                "s3:DeleteObject"
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*",
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelations*",
                       "arn:aws:s3:::cc-spotify-clone-images-bucket/songs/*",
                       "arn:aws:s3:::cc-spotify-clone-images-bucket/covers/*"
            ]
        ))

        retry_lambda = aws_lambda.Function(
            self, "RetryTranscriptionLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="retry_transcription.handler",
            code=aws_lambda.Code.from_asset("lambda/transcription/retry"),
            layers=[shared_layer],
            timeout=Duration.seconds(60),
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name
            }
        )

        transcription_retry_queue = sqs.Queue(
            self, "TranscriptionRetryQueue",
            visibility_timeout=Duration.minutes(5),
            retention_period=Duration.days(7),
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3, # max number of retries
                queue=sqs.Queue(self, "TranscriptionDLQ")
            )
        )

        transcription_lambda = aws_lambda.Function(
            self, "StartTranscriptionLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="start_transcription.handler",
            layers=[shared_layer],
            code=aws_lambda.Code.from_asset("lambda/transcription/create"),
            timeout=Duration.seconds(60),
            environment={
                "MEDIA_BUCKET": self.images_bucket.bucket_name,
                "RETRY_QUEUE_URL": transcription_retry_queue.queue_url
            }
        )

        transcription_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "transcribe:StartTranscriptionJob",
                    "transcribe:GetTranscriptionJob",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:ListBucket"
                ],
                resources=["*"],
            )
        )

        retry_lambda.add_event_source(
            lambda_events.SqsEventSource(
                transcription_retry_queue,
                batch_size=1
            )
        )

        self.images_bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(transcription_lambda)
        )

        get_discover_page.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:Query",
                "dynamodb:Scan",
                "dynamodb:GetItem",
                "s3:GetObject"
            ],
            resources=[
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists*",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelations*",
                "arn:aws:s3:::cc-spotify-clone-images-bucket/songs/*",
                "arn:aws:s3:::cc-spotify-clone-images-bucket/covers/*"
            ]
        ))

        song_api = api.root.add_resource("songs")
        song_api.add_method("POST", apigw.LambdaIntegration(create_song_lambda), authorizer=authorizer)
        song_id_resource = song_api.add_resource("{id}")
        song_id_resource.add_method("GET", apigw.LambdaIntegration(get_song_lambda), authorizer=authorizer)
        song_id_resource.add_method("DELETE", apigw.LambdaIntegration(delete_song_lambda), authorizer=authorizer)

        album_api = api.root.add_resource("albums")
        album_api.add_method("POST", apigw.LambdaIntegration(create_album_lambda), authorizer=authorizer)

        album_id_resource = album_api.add_resource("{id}")
        album_id_resource.add_method("GET", apigw.LambdaIntegration(get_album_lambda), authorizer=authorizer)
        album_id_resource.add_method("DELETE", apigw.LambdaIntegration(delete_album_lambda), authorizer=authorizer)

        transcription_api = api.root.add_resource("transcriptions")
        transcription_id_resource = transcription_api.add_resource("{id}")
        transcription_id_resource.add_method("GET", apigw.LambdaIntegration(get_transcription_lambda), authorizer=authorizer)

        discover_root = api.root.add_resource("discover")
        discover_genre = discover_root.add_resource("{genre}")
        discover_genre.add_method(
            "GET",
            apigw.LambdaIntegration(get_discover_page),
            authorizer=authorizer
        )

        get_song_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:BatchGetItem",
                "s3:GetObject",
                "s3:ListBucket"
            ],
            resources=[
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists*",
                "arn:aws:s3:::cc-spotify-clone-images-bucket/songs/*",
                "arn:aws:s3:::cc-spotify-clone-images-bucket/covers/*",
                "arn:aws:s3:::cc-spotify-clone-images-bucket/transcriptions/*",
                "arn:aws:s3:::cc-spotify-clone-images-bucket"
            ]
        ))

        get_transcription_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:ListBucket"],
                resources=["arn:aws:s3:::cc-spotify-clone-images-bucket"]
            )
        )

        get_transcription_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject"],
                resources=["arn:aws:s3:::cc-spotify-clone-images-bucket/transcriptions/*"]
            )
        )

        get_album_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:Query",
                "s3:GetObject",
                "s3:ListBucket",
                "dynamodb:BatchGetItem"
            ],
            resources=[
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists*",
                "arn:aws:s3:::cc-spotify-clone-images-bucket/songs/*",
                "arn:aws:s3:::cc-spotify-clone-images-bucket/covers/*"
            ]
        ))

        CfnOutput(self, "AudioBucketName", value=audio_bucket.bucket_name)
        CfnOutput(self, "ImagesBucketName", value=self.images_bucket.bucket_name)
