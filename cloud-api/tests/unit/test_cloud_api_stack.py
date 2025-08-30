import aws_cdk as core
import aws_cdk.assertions as assertions

from spotify_clone_api.spotify_clone_stack import SpotifyCloneStack

# example tests. To run these tests, uncomment this file along with the example
# resource in spotify_clone_api/spotify_clone_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = SpotifyCloneStack(app, "cloud-api")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
