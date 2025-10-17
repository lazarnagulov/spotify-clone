from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb, RemovalPolicy, aws_lambda,
    aws_apigateway as apigw
)
from constructs import Construct


class SubscriptionStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, shared_layer, api, authorizer,  **kwargs) -> None:
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

        subscription_table.grant_read_write_data(subscribe_lambda)

        subscribe_api = api.root.add_resource("subscription")
        subscribe_api.add_method("POST", apigw.LambdaIntegration(subscribe_lambda), authorizer=authorizer)
