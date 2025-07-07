import aws_cdk as core
import aws_cdk.assertions as assertions

from cloud_api.cloud_api_stack import CloudApiStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cloud_api/cloud_api_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CloudApiStack(app, "cloud-api")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
