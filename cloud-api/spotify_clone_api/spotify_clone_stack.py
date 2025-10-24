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

        genre_relations_table = dynamodb.Table(
            self, "GenreRelationsTable",
            table_name="GenreRelations",
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

        self.music_catalog_table = dynamodb.Table(
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
            removal_policy=RemovalPolicy.DESTROY,
            stream=dynamodb.StreamViewType.NEW_IMAGE,
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
                'ARTISTS_TABLE': artists_table.table_name,
                'MUSIC_CATALOG': "MusicCatalog",
                "GENRE_RELATIONS_TABLE": genre_relations_table.table_name
            }
        )

        delete_artist_lambda = aws_lambda.Function(
            self,
            "DeleteArtistFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="delete_artist.handler",
            code=aws_lambda.Code.from_asset("lambda/artist/delete"),
            layers=[shared_layer],
            environment={
                'ARTISTS_TABLE': artists_table.table_name,
                "GENRE_RELATIONS_TABLE": genre_relations_table.table_name,
                "SUBSCRIPTION_TABLE": "Subscriptions"
            }
        )

        get_all_artists_lambda = aws_lambda.Function(
            self,
            "GetAllArtistsFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_all_artists.handler",
            code=aws_lambda.Code.from_asset("lambda/artist/get_all"),
            layers=[shared_layer],
            environment={
                'ARTISTS_TABLE': artists_table.table_name
            }
        )

        edit_artist_lambda = aws_lambda.Function(
            self,
            "EditArtistFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="edit_artist.handler",
            code=aws_lambda.Code.from_asset("lambda/artist/edit"),
            layers=[shared_layer],
            environment={
                'ARTISTS_TABLE': artists_table.table_name,
                'GENRE_RELATIONS_TABLE': genre_relations_table.table_name,
            }
        )

        artist_api = api.root.add_resource("artists")
        artist_api.add_method("POST", apigw.LambdaIntegration(create_artist_lambda), authorizer=authorizer)
        artist_api.add_method("GET", apigw.LambdaIntegration(get_all_artists_lambda), authorizer=authorizer)

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

        artist_id_resource = artist_api.add_resource("{id}")
        artist_id_resource.add_method("GET", apigw.LambdaIntegration(get_artist_details_lambda))
        artist_id_resource.add_method("DELETE", apigw.LambdaIntegration(delete_artist_lambda), authorizer=authorizer)
        artist_id_resource.add_method("PUT", apigw.LambdaIntegration(edit_artist_lambda), authorizer=authorizer)

        create_artist_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:BatchWriteItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:GetItem"
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists*",
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/MusicCatalog*",
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelations*"]
        ))

        get_all_artists_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:Scan"
            ],
            resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists*"]
        ))

        edit_artist_lambda.role.add_to_policy(iam.PolicyStatement(
            actions=[
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:BatchWriteItem",
                "dynamodb:UpdateItem"
            ],
             resources=[f"arn:aws:dynamodb:{self.region}:{self.account}:table/Artists*",
                       f"arn:aws:dynamodb:{self.region}:{self.account}:table/GenreRelations*"]
        ))

        get_genres_lambda = aws_lambda.Function(
            self,
            "GetGenresFunction",
            runtime=aws_lambda.Runtime.PYTHON_3_11,
            handler="get_genres.handler",
            code=aws_lambda.Code.from_asset("lambda/genre"),
            layers=[shared_layer],
            environment={
                'GENRES_TABLE': genres_table.table_name
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

        delete_artist_lambda.add_to_role_policy(
          iam.PolicyStatement(
            actions=[
              "dynamodb:GetItem",
              "dynamodb:DeleteItem",
              "dynamodb:BatchWriteItem",
              "dynamodb:Query"
            ],
          resources=[
              artists_table.table_arn,
              genre_relations_table.table_arn,
              f"arn:aws:dynamodb:{self.region}:{self.account}:table/Subscriptions*",
          ],
    )
)
