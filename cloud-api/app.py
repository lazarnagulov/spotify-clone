#!/usr/bin/env python3
import os

import aws_cdk as cdk

from spotify_clone_api.api_gateway_stack import ApiGatewayStack
from spotify_clone_api.cognito_stack import CognitoStack
from spotify_clone_api.spotify_clone_stack import SpotifyCloneStack

REGION = 'eu-central-1'

app = cdk.App()
env = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=REGION,
)

cognito_stack = CognitoStack(app, "CognitoStack", env=env)
api_stack = ApiGatewayStack(app, "ApiStack", cognito_stack.user_pool, env=env)

SpotifyCloneStack(app, "CloudApiStack")

app.synth()
