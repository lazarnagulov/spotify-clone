from aws_cdk import (
    Stack,
    aws_apigateway as apigw
)
from constructs import Construct


class ApiGatewayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, user_pool, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        #
        # self.authorizer = apigw.CognitoUserPoolsAuthorizer(
        #     self, "CognitoAuthorizer",
        #     cognito_user_pools=[user_pool]
        # )
