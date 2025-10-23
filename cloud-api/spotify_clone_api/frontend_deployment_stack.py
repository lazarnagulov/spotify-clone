import os
from aws_cdk import Stack, RemovalPolicy
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as cforigins
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_s3_deployment as s3_deployment
from constructs import Construct

class FrontendDeploymentStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        deployment_bucket = s3.Bucket(
            self,
            "FrontDeploymentBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=cforigins.S3Origin(deployment_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                )
            ]
        )

        angular_build_path = os.path.join(os.getcwd(), "../frontend/dist/frontend/browser")
        s3_deployment.BucketDeployment(
            self,
            "DeployFrontApp",
            sources=[s3_deployment.Source.asset(angular_build_path)],
            destination_bucket=deployment_bucket,
            distribution=distribution,
            distribution_paths=["/*"]
        )