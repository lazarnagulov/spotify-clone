from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb, RemovalPolicy, aws_lambda,
    aws_apigateway as apigw,
    aws_iam as iam
)
from constructs import Construct


class SubscriptionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, shared_layer, api, authorizer, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        subscription_table = dynamodb.Table(
            self, "SubscriptionsTable",
            table_name="Subscriptions",
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
            removal_policy=RemovalPolicy.DESTROY
        )

        subscribe_lambda = aws_lambda.Function(
            self, "SubscribeFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="subscribe.handler",
            code=aws_lambda.Code.from_asset("lambda/subscription/subscribe"),
            layers=[shared_layer],
            environment={
                "SUBSCRIPTION_TABLE": subscription_table.table_name
            }
        )

        unsubscribe_lambda = aws_lambda.Function(
            self, "UnsubscribeFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="unsubscribe.handler",
            code=aws_lambda.Code.from_asset("lambda/subscription/unsubscribe"),
            layers=[shared_layer],
            environment={
                "SUBSCRIPTION_TABLE": subscription_table.table_name
            }
        )

        check_lambda = aws_lambda.Function(
            self, "CheckSubscriptionFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="check_subscription.handler",
            code=aws_lambda.Code.from_asset("lambda/subscription/check"),
            layers=[shared_layer],
            environment={
                "SUBSCRIPTION_TABLE": subscription_table.table_name
            }
        )

        all_subscriptions_lambda = aws_lambda.Function(
            self, "GetAllSubscriptionFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_all_subscriptions.handler",
            code=aws_lambda.Code.from_asset("lambda/subscription/get_all"),
            layers=[shared_layer],
            environment={
                "SUBSCRIPTION_TABLE": subscription_table.table_name,
                "ARTISTS_TABLE": "Artists",
                "GENRES_TABLE": "Genres",
            }
        )


        subscription_table.grant_read_write_data(subscribe_lambda)
        subscription_table.grant_read_write_data(unsubscribe_lambda)
        subscription_table.grant_read_data(check_lambda)
        subscription_table.grant_read_data(all_subscriptions_lambda)

        all_subscriptions_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:GetItem",
                "dynamodb:Query"
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists*",
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelations*"]
        ))

        subscription_api = api.root.add_resource("subscription")

        subscription_api.add_method("POST", apigw.LambdaIntegration(subscribe_lambda), authorizer=authorizer)
        subscription_api.add_method("DELETE", apigw.LambdaIntegration(unsubscribe_lambda), authorizer=authorizer)
        subscription_api.add_method("GET", apigw.LambdaIntegration(check_lambda), authorizer=authorizer)

        all_subscriptions_api = api.root.add_resource("subscriptions")
        all_subscriptions_api.add_method("GET", apigw.LambdaIntegration(all_subscriptions_lambda), authorizer=authorizer)
