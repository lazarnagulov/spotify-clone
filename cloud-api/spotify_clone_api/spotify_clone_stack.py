from aws_cdk import (
    Stack, aws_lambda,
    aws_apigateway as apigw,
)
from constructs import Construct

class SpotifyCloneStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cognito_env = {
            "LOG_LEVEL": "DEBUG",
            "COGNITO_REGION": "eu-central-1",
            "COGNITO_CLIENT_ID": "40q842ul1ip3m7n0eb2tg61g2t",
            "COGNITO_USER_POOL_ID": "eu-central-1_jtrzQHN3l"
        }

        # TODO: Add cognito user pool creation?

        shared_layer = aws_lambda.LayerVersion(
            self, "SharedDependenciesLayer",
            code=aws_lambda.Code.from_asset(".build/shared.zip"),
            description="Shared dependencies (pydantic, logger)",
            compatible_runtimes = [aws_lambda.Runtime.PYTHON_3_11]
        )

        registration = aws_lambda.Function(
            self,
            "RegisterFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="register.handler",
            code=aws_lambda.Code.from_asset("lambda/auth/register"),
            layers=[shared_layer],
            environment=cognito_env,
        )

        confirmation = aws_lambda.Function(
            self,
            "ConfirmationFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="confirm.handler",
            code=aws_lambda.Code.from_asset("lambda/auth/confirm"),
            layers=[shared_layer],
            environment=cognito_env,
        )

        login = aws_lambda.Function(
            self,
            "LoginFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="login.handler",
            code=aws_lambda.Code.from_asset("lambda/auth/login"),
            layers=[shared_layer],
            environment=cognito_env,
        )

        api = apigw.RestApi(self, "SpotifyCloneApi")
        register = api.root.add_resource("registration")
        confirm = api.root.add_resource("confirmation")
        login_ep = api.root.add_resource("login")

        register.add_method("POST", apigw.LambdaIntegration(registration))
        confirm.add_method("POST", apigw.LambdaIntegration(confirmation))
        login_ep.add_method("POST", apigw.LambdaIntegration(login))