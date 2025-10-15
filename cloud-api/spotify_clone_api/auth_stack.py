from aws_cdk import (
    Stack,
    aws_lambda,
    aws_apigateway as apigw,
    aws_iam as iam,
)


class AuthStack(Stack):

    def __init__(self, scope, construct_id: str, api, shared_layer_arn, cognito_client_id, user_pool,  **kwargs) -> None:
        super().__init__(scope, construct_id,   **kwargs)
        shared_layer = aws_lambda.LayerVersion.from_layer_version_arn(self, "ImportedSharedLayer", shared_layer_arn)

        cognito_env = {
            "LOG_LEVEL": "DEBUG",
            "COGNITO_REGION": "eu-central-1",
            "COGNITO_CLIENT_ID": cognito_client_id,
            "COGNITO_USER_POOL_ID": user_pool.user_pool_id
        }

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

        refresh = aws_lambda.Function(
            self,
            "RefreshFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="refresh.handler",
            code=aws_lambda.Code.from_asset("lambda/auth/refresh"),
            layers=[shared_layer],
            environment=cognito_env,
        )

        register_api = api.root.add_resource("registration")
        confirm_api = api.root.add_resource("confirmation")
        login_api = api.root.add_resource("login")
        refresh_api = api.root.add_resource("refresh")

        register_api.add_method("POST", apigw.LambdaIntegration(registration))
        confirm_api.add_method("POST", apigw.LambdaIntegration(confirmation))
        login_api.add_method("POST", apigw.LambdaIntegration(login))
        refresh_api.add_method("POST", apigw.LambdaIntegration(refresh))

        registration.role.add_to_policy(iam.PolicyStatement(
            actions=["cognito-idp:AdminAddUserToGroup"],
            resources=[
                f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{cognito_env['COGNITO_USER_POOL_ID']}"
            ]
        ))

        for fn in [login, refresh]:
            fn.role.add_to_policy(iam.PolicyStatement(
                actions=[
                    "cognito-idp:InitiateAuth",
                    "cognito-idp:RespondToAuthChallenge",
                    "cognito-idp:AdminInitiateAuth"
                ],
                resources=[
                    f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{cognito_env['COGNITO_USER_POOL_ID']}"
                ]
            ))