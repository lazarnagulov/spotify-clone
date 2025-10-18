from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb, RemovalPolicy, aws_lambda,
    aws_apigateway as apigw
)
from constructs import Construct


class RatingsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, shared_layer, api, authorizer, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ratings_table = dynamodb.Table(
            self, "RatingsTable",
            table_name="Ratings",
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

        create_rating_lambda = aws_lambda.Function(
            self, "SubscribeFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="create_rating.handler",
            code=aws_lambda.Code.from_asset("lambda/rating/create"),
            layers=[shared_layer],
            environment={
                "RATINGS_TABLE": ratings_table.table_name
            }
        )

        ratings_table.grant_read_write_data(create_rating_lambda)
        subscription_api = api.root.add_resource("ratings")

        subscription_api.add_method("POST", apigw.LambdaIntegration(create_rating_lambda), authorizer=authorizer)