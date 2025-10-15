from aws_cdk import (
    aws_lambda,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy,
    Stack
)
from constructs import Construct

class SpotifyCloneStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, authorizer, shared_layer, api, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

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
            code=aws_lambda.Code.from_asset("lambda/artist"),
            layers=[shared_layer],
            environment={
                'TABLE_NAME': artists_table.table_name
            }
        )

        artist_creation = api.root.add_resource("artists")
        artist_creation.add_method("POST", apigw.LambdaIntegration(create_artist_lambda), authorizer=authorizer)

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
