import os

import boto3

COGNITO_REGION = os.environ.get("COGNITO_REGION")

client = boto3.client('cognito-idp', region_name=COGNITO_REGION)


def handler(event, _context):
    user_pool_id = event['userPoolId']
    username = event['userName']

    client.admin_add_user_to_group(
        UserPoolId=user_pool_id,
        Username=username,
        GroupName="user"
    )

    return event