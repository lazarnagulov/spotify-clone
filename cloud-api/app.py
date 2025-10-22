#!/usr/bin/env python3
import os

import aws_cdk as cdk

from spotify_clone_api.api_gateway_stack import ApiGatewayStack
from spotify_clone_api.auth_stack import AuthStack
from spotify_clone_api.cognito_stack import CognitoStack
from spotify_clone_api.content_stack import ContentStack
from spotify_clone_api.layer_stack import LayerStack
from spotify_clone_api.ratings_stack import RatingsStack
from spotify_clone_api.spotify_clone_stack import SpotifyCloneStack
from spotify_clone_api.subscription_stack import SubscriptionStack
from spotify_clone_api.listening_history_stack import ListeningHistoryStack
from spotify_clone_api.feed_stack import UserFeedStack

REGION = 'eu-central-1'

app = cdk.App()
env = cdk.Environment(
    account=os.environ["CDK_DEFAULT_ACCOUNT"],
    region=REGION,
)

layer_stack = LayerStack(app, "SpotifyCloneLayerStack", env=env)

cognito_stack = CognitoStack(
    app,
    "CognitoStack",
    env=env

)
gw_stack = ApiGatewayStack(app, "SpotifyCloneApiGatewayStack", user_pool=cognito_stack.user_pool,  env=env)
auth_stack = AuthStack(
    app,
    "SpotifyCloneAuthStack",
    api=gw_stack.api,
    cognito_client_id=cognito_stack.app_client.user_pool_client_id,
    shared_layer=layer_stack.shared_layer,
    user_pool=cognito_stack.user_pool,
    env=env
)

subscriptions_stack = SubscriptionStack(
    app,
    "SpotifyCloneSubscriptionStack",
    shared_layer=layer_stack.shared_layer,
    authorizer=gw_stack.authorizer,
    api=gw_stack.api,
    env=env
)

ratings_stack = RatingsStack(
    app,
    "SpotifyCloneRatingsStack",
    shared_layer=layer_stack.shared_layer,
    authorizer=gw_stack.authorizer,
    api=gw_stack.api,
    env=env
)

listening_history_stack = ListeningHistoryStack(
      app,
      "SpotifyCloneListeningHistoryStack",
      shared_layer=layer_stack.shared_layer,
      authorizer=gw_stack.authorizer,
      api=gw_stack.api,
      env=env
)

table_stack = SpotifyCloneStack(
    app,
    "CloudApiStack",
    shared_layer=layer_stack.shared_layer,
    authorizer=gw_stack.authorizer,
    api=gw_stack.api,
    env=env
)

content_stack = ContentStack(
    app,
    "SpotifyCloneContentStack",
    shared_layer=layer_stack.shared_layer,
    authorizer=gw_stack.authorizer,
    api=gw_stack.api,
    notify_subscribers_fn=subscriptions_stack.notify_subscribers_lambda,
    env=env
)

feed_stack = UserFeedStack(
      app,
      "SpotifyCloneUserFeedStack",
      shared_layer=layer_stack.shared_layer,
      authorizer=gw_stack.authorizer,
      api=gw_stack.api,
      ratings_table=ratings_stack.ratings_table,
      subscriptions_table=subscriptions_stack.subscription_table,
      listening_history_table=listening_history_stack.listening_history_table,
      music_catalog_table=table_stack.music_catalog_table,
      media_bucket=content_stack.images_bucket,
      env=env
)

app.synth()
