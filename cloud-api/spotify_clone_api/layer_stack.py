from aws_cdk import Stack, aws_lambda, CfnOutput
from constructs import Construct


class LayerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        shared_layer = aws_lambda.LayerVersion(
            self, "SharedDependenciesLayer",
            code=aws_lambda.Code.from_asset(".build/shared.zip"),
            description="Shared dependencies (pydantic, logger)",
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11]
        )

        content_layer = aws_lambda.LayerVersion(
            self, "ContentDependenciesLayer",
            code=aws_lambda.Code.from_asset(".build/content.zip"),
            description="Libraries required for songs",
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_11]
        )

        self.shared_layer_arn = shared_layer.layer_version_arn
        self.content_layer_arn = content_layer.layer_version_arn

