from aws_cdk import (
    Stack, aws_lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy,
    Stack
)
from constructs import Construct


def add_options(resource: apigw.Resource):
    resource.add_method(
        "OPTIONS",
        apigw.MockIntegration(
            integration_responses=[{
                "statusCode": "200",
                "responseParameters": {
                    "method.response.header.Access-Control-Allow-Origin": "'http://localhost:4200'",
                    "method.response.header.Access-Control-Allow-Credentials": "'true'",
                    "method.response.header.Access-Control-Allow-Headers": "'Content-Type,Authorization'",
                    "method.response.header.Access-Control-Allow-Methods": "'OPTIONS,GET,POST'",
                },
            }],
            passthrough_behavior=apigw.PassthroughBehavior.WHEN_NO_MATCH,
            request_templates={"application/json": '{"statusCode": 200}'},
        ),
        method_responses=[{
            "statusCode": "200",
            "responseParameters": {
                "method.response.header.Access-Control-Allow-Origin": True,
                "method.response.header.Access-Control-Allow-Credentials": True,
                "method.response.header.Access-Control-Allow-Headers": True,
                "method.response.header.Access-Control-Allow-Methods": True,
            },
        }],
    )


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

        refresh = aws_lambda.Function(
            self,
            "RefreshFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="refresh.handler",
            code=aws_lambda.Code.from_asset("lambda/auth/refresh"),
            layers=[shared_layer],
            environment=cognito_env,
        )

        api = apigw.RestApi(self, "SpotifyCloneApi")
        register = api.root.add_resource("registration")
        confirm = api.root.add_resource("confirmation")
        login_resource = api.root.add_resource("login")
        refresh_resource = api.root.add_resource("refresh")

        register.add_method("POST", apigw.LambdaIntegration(registration))
        confirm.add_method("POST", apigw.LambdaIntegration(confirmation))
        login_resource.add_method("POST", apigw.LambdaIntegration(login))
        refresh_resource.add_method("POST", apigw.LambdaIntegration(refresh))

        genres_table = dynamodb.Table(
            self, "GenresTable",
            table_name="Genres",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY
        )

        music_catalog_table = dynamodb.Table(
            self, "MusicCatalogTable",
            table_name="MusicCatalog",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY
        )

        artists_table = dynamodb.Table(
            self, "ArtistsTable",
            table_name="Artists",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            read_capacity=1,
            write_capacity=1,
            removal_policy=RemovalPolicy.DESTROY
        )

        create_artist_lambda = aws_lambda.Function(
            self,
            "CreateArtistFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="create_artist.handler",
            code=aws_lambda.Code.from_asset("lambda/artist/create"),
            layers=[shared_layer],
            environment={
                'TABLE_NAME': artists_table.table_name
            }
        )

        get_artist_details_lambda = aws_lambda.Function(
            self,
            "GetArtistDetailsFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_artist.handler",
            code=aws_lambda.Code.from_asset("lambda/artist/get"),
            layers=[shared_layer],
            environment={
                'TABLE_NAME': artists_table.table_name
            }
        )
        artists_table.grant_read_data(get_artist_details_lambda)

        artist_resource = api.root.add_resource("artists")
        artist_resource.add_method("POST", apigw.LambdaIntegration(create_artist_lambda))

        artist_id_resource = artist_resource.add_resource("{id}", default_cors_preflight_options=apigw.CorsOptions(
            allow_origins=["http://localhost:4200"],
            allow_methods=["OPTIONS", "GET"],
            allow_headers=["Content-Type", "Authorization"],
            allow_credentials=True
        ))
        artist_id_resource.add_method("GET", apigw.LambdaIntegration(get_artist_details_lambda))

        for resource in [register, confirm, login_resource, refresh_resource, artist_resource]:
            add_options(resource)

        create_artist_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:GetItem"
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists*",
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*"]
        ))

        get_genres_lambda = aws_lambda.Function(
            self,
            "GetGenresFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_genres.handler",
            code=aws_lambda.Code.from_asset("lambda/genre"),
            layers=[shared_layer],
            environment={
                'TABLE_NAME': genres_table.table_name
            }
        )

        genres = api.root.add_resource("genres")
        genres.add_method("GET", apigw.LambdaIntegration(get_genres_lambda))

        get_genres_lambda.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=[genres_table.table_arn]
            )
        )

        registration.role.add_to_policy(iam.PolicyStatement(
            actions=["cognito-idp:AdminAddUserToGroup"],
            resources=[
                f"arn:aws:cognito-idp:{self.region}:{self.account}:userpool/{cognito_env['COGNITO_USER_POOL_ID']}"
            ]
        ))