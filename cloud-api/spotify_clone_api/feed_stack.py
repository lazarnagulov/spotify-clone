from aws_cdk import (
    Stack,
    Duration,
    aws_iam as iam,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_lambda,
    aws_lambda_event_sources as lambda_event_sources,
    aws_sqs as sqs,
    RemovalPolicy,
    Duration
)
from constructs import Construct


class UserFeedStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, shared_layer, api, authorizer, ratings_table, subscriptions_table, listening_history_table, music_catalog_table, media_bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        user_feed_table = dynamodb.Table(
            self, "UserFeedTable",
            table_name="UserFeed",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY,
        )

        create_user_feed_lambda = aws_lambda.Function(
          self, "CreateUserFeedFunction",
          runtime=aws_lambda.Runtime.PYTHON_3_11,
          handler="create_feed.handler",
          code=aws_lambda.Code.from_asset("lambda/feed/create"),
          layers=[shared_layer],
          environment={
              "USER_FEED": user_feed_table.table_name,
          }
        )

        create_user_feed_lambda.role.add_to_policy( # TODO: DELETE UNNECESSARY
        iam.PolicyStatement(
            actions=[
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:GetItem",
                "dynamodb:BatchGetItem"
            ],
            resources=[
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/UserFeed",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/RatingsTable",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/ListeningHistoryTable",
                f"arn:aws:dynamodb:{self.region}:{self.account}:table/SubscriptionsTable"
            ]
         )
      )

        feed_queue = sqs.Queue(
            self, "FeedQueue",
            queue_name="FeedQueue",
            visibility_timeout=Duration.seconds(60),
        )

        get_user_feed_lambda = aws_lambda.Function(
            self, "GetUserFeedFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_user_feed.handler",
            code=aws_lambda.Code.from_asset("lambda/feed/get"),
            layers=[shared_layer],
            timeout=Duration.seconds(15),
            environment={
                "USER_FEED": user_feed_table.table_name,
                "SONGS_TABLE": music_catalog_table.table_name,
                "MEDIA_BUCKET": media_bucket.bucket_name, 
            }
        )

        get_user_feed_lambda.role.add_to_policy(iam.PolicyStatement( # TODO: DELETE UNNECESSARY
          actions=[
              "dynamodb:GetItem",
              "dynamodb:Query",
              "dynamodb:BatchGetItem",
              "s3:GetObject"
          ],
        resources=[
            f"arn:aws:dynamodb:{self.region}:{self.account}:table/UserFeed",
            f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog",
            f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists",
            "arn:aws:s3:::cc-spotify-clone-images-bucket/songs/*",
            "arn:aws:s3:::cc-spotify-clone-images-bucket/covers/*"
        ]))


        feed_trigger_lambda = aws_lambda.Function(
            self, "FeedTriggerLambda",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="feed_trigger.handler",
            code=aws_lambda.Code.from_asset("lambda/feed/trigger"),
            layers=[shared_layer],
            environment={
                "FEED_SQS_URL": feed_queue.queue_url
            }
        )

        feed_trigger_lambda.add_event_source(
            lambda_event_sources.DynamoEventSource(
                ratings_table,
                starting_position=aws_lambda.StartingPosition.LATEST,
                batch_size=5,
                enabled=True
            )
        )

        feed_trigger_lambda.add_event_source(
            lambda_event_sources.DynamoEventSource(
                listening_history_table,
                starting_position=aws_lambda.StartingPosition.LATEST,
                batch_size=5,
                enabled=True
            )
        )

        feed_trigger_lambda.add_event_source(
            lambda_event_sources.DynamoEventSource(
                subscriptions_table,
                starting_position=aws_lambda.StartingPosition.LATEST,
                batch_size=5,
                enabled=True
            )
        )

        feed_trigger_lambda.add_event_source( 
            lambda_event_sources.DynamoEventSource(
                music_catalog_table,
                starting_position=aws_lambda.StartingPosition.LATEST,
                batch_size=5,
                enabled=True
            )
        )
        
        feed_queue.grant_send_messages(feed_trigger_lambda)
        user_feed_table.grant_read_write_data(create_user_feed_lambda)
        create_user_feed_lambda.add_event_source(lambda_event_sources.SqsEventSource(feed_queue))

        user_feed_api = api.root.add_resource("feed")
        user_feed_api.add_method("GET", apigw.LambdaIntegration(get_user_feed_lambda), authorizer=authorizer)
