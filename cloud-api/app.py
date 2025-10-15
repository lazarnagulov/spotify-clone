#!/usr/bin/env python3
import os

import aws_cdk as cdk

from spotify_clone_api.api_gateway_stack import ApiGatewayStack
from spotify_clone_api.auth_stack import AuthStack
from spotify_clone_api.cognito_stack import CognitoStack
from spotify_clone_api.content_stack import ContentStack
from spotify_clone_api.layer_stack import LayerStack
from spotify_clone_api.spotify_clone_stack import SpotifyCloneStack

REGION = 'eu-central-1'

app = cdk.App()
env = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=REGION,
)

layer_stack = LayerStack(app, "SpotifyCloneLayerStack", env=env)

cognito_stack = CognitoStack(app, "CognitoStack", env=env)
gw_stack = ApiGatewayStack(app, "SpotifyCloneApiGatewayStack", env=env)
AuthStack(app, "SpotifyCloneAuthStack", api=gw_stack.api, shared_layer_arn=layer_stack.shared_layer_arn, env=env)

table_stack = SpotifyCloneStack(
    app,
    "CloudApiStack",
    shared_layer_arn=layer_stack.shared_layer_arn,
    api=gw_stack.api,
    env=env
)

content_stack = ContentStack(
    app,
    "SpotifyCloneContentStack",
    shared_layer_arn=layer_stack.shared_layer_arn,
    api=gw_stack.api,
    env=env
)


app.synth()
