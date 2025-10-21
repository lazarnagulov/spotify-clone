from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb, RemovalPolicy, aws_lambda,
    aws_apigateway as apigw
)
from constructs import Construct

class ListeningHistoryStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, shared_layer, api, authorizer, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        listening_history_table = dynamodb.Table(
            self, "ListeningHistoryTable",
                  table_name="ListeningHistory",
                  partition_key=dynamodb.Attribute(
                      name="PK",
                      type=dynamodb.AttributeType.STRING
                  ),
                  sort_key=dynamodb.Attribute(
                      name="SK",
                      type=dynamodb.AttributeType.NUMBER
                  ),
                  read_capacity=1,
                  write_capacity=1,
                  removal_policy=RemovalPolicy.DESTROY
              )
        
        create_listening_history_lambda = aws_lambda.Function(
            self, "CreateListeningHistoryFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="create_listening_history.handler",
            code=aws_lambda.Code.from_asset("lambda/listening_history/create"),
            layers=[shared_layer],
            environment={
                "LISTENING_HISTORY": listening_history_table.table_name,
            }
        )
        
        listening_history_table.grant_read_write_data(create_listening_history_lambda)
        listening_history_api = api.root.add_resource("listening-history")
        listening_history_api.add_method("POST", apigw.LambdaIntegration(create_listening_history_lambda), authorizer=authorizer)
