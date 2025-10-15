
from aws_cdk import Stack, RemovalPolicy, aws_cognito as cognito, CfnOutput
from aws_cdk.aws_cognito import AuthFlow, UserPoolGroup
from aws_cdk.aws_iam import ManagedPolicy
from aws_cdk.aws_lambda import Function, Runtime, Code
from constructs import Construct


class CognitoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        post_confirm_lambda = Function(
            self,
            "PostConfirmationLambda",
            runtime=Runtime.PYTHON_3_11,
            handler="post_confirm.handler",
            code=Code.from_asset("lambda/auth/post_confirm"),
            environment={
                "COGNITO_REGION": "eu-central-1"
            }
        )

        post_confirm_lambda.role.add_managed_policy(
            ManagedPolicy.from_aws_managed_policy_name("AmazonCognitoPowerUser")
        )

        self.user_pool = cognito.UserPool(
            self, "SpotifyCloneUserPool",
            self_sign_up_enabled=True,
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            sign_in_aliases=cognito.SignInAliases(email=True),
            lambda_triggers=cognito.UserPoolTriggers(
                post_confirmation=post_confirm_lambda
            ),
            removal_policy=RemovalPolicy.DESTROY
        )

        self.app_client = cognito.UserPoolClient(
            self, "SpotifyCloneAppClient",
            user_pool=self.user_pool,
            generate_secret=False,
            auth_flows=AuthFlow(user_password=True)
        )
        UserPoolGroup(
            self,
            "AuthenticatedUserGroup",
            user_pool=self.user_pool,
            group_name="user",
            description="Standard user group"
        )

        UserPoolGroup(
            self,
            "AdminGroup",
            user_pool=self.user_pool,
            group_name="admin",
            description="Administrator group"
        )


        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=self.app_client.user_pool_client_id)