from aws_cdk import (
    Stack, aws_lambda,
    aws_apigateway as apigw,
)
from constructs import Construct

class SpotifyCloneStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        shared_layer = aws_lambda.LayerVersion(
            self, "SharedDependenciesLayer",
            code=aws_lambda.Code.from_asset(".build/shared.zip"),
            description="Shared dependencies (pydantic, logger)",
            compatible_runtimes = [aws_lambda.Runtime.PYTHON_3_11]
        )

        register = aws_lambda.Function(
            self,
            "RegisterFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="register.handler",
            code=aws_lambda.Code.from_asset("lambda/auth"),
            layers=[shared_layer],
            environment={
                "LOG_LEVEL": "DEBUG"
            },
        )

        api = apigw.RestApi(self, "SpotifyCloneApi")
        auth = api.root.add_resource("register")

        auth.add_method("POST", apigw.LambdaIntegration(register))
