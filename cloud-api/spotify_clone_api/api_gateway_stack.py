
from aws_cdk import (
    Stack,
    aws_apigateway as apigw
)



class ApiGatewayStack(Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # self.authorizer = apigw.CognitoUserPoolsAuthorizer(
        #     self, "CognitoAuthorizer",
        #     cognito_user_pools=[cognito_user_pool]
        # )

        self.api = apigw.RestApi(
            self, "SpotifyCloneApi",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=["http://localhost:4200"],
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["Content-Type", "Authorization"],
                allow_credentials=True
            )
        )