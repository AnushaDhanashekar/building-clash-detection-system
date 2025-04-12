from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
aws_apigateway as apigateway,
aws_sqs as sqs,
    Duration,CfnOutput
)
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk.aws_lambda_event_sources import SqsEventSource  # <-- Correct import for event sources

from constructs import Construct

class BuildingClashesStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # SQS Queue for task submission
        self.sqs_queue = sqs.Queue(
            self, "TaskQueue",
            queue_name="TaskQueue"
        )
        # Simple Lambda to handle POST requests and SQS submission
        self.handle_post_sqs_lambda_fn = lambda_.DockerImageFunction(
            self, "BuildingClashLambda",
            code=lambda_.DockerImageCode.from_image_asset(
                directory=".",   # assumes Dockerfile is in the root
                file="Dockerfile",
                exclude=["cdk.out", "node_modules"],
                build_args={  # Docker build arguments, set the platform here
                    'PLATFORM': 'linux/amd64',  # specify platform here
                }
            ),
            architecture=lambda_.Architecture.ARM_64,
            memory_size=1024,
            timeout=Duration.seconds(30)
        )

        # Simple Lambda to handle POST requests and SQS submission
        self.building_clash_docker_lambda = lambda_.Function(
            self, "SimpleLambda",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="building_clash_lambda_handler.handler",  # Adjust this based on your function handler
            code=lambda_.Code.from_asset("pycontrollers/lambdas"),  # Directory with the building_clash_docker_lambda.py code
            environment={
                "SQS_QUEUE_URL": self.sqs_queue.queue_url,
                # "DYNAMODB_TABLE_NAME": self.dynamodb_table.table_name
            },
        timeout = Duration.seconds(10)
        )

        # Allow the simple Lambda to write to SQS
        self.sqs_queue.grant_send_messages(self.building_clash_docker_lambda)
        # Create event source mapping to trigger the simple Lambda from the SQS queue
        self.handle_post_sqs_lambda_fn.add_event_source(SqsEventSource(self.sqs_queue))

        # API Gateway to expose the service
        api = apigateway.RestApi(self, "TaskApi",
                                 rest_api_name="Task API",
                                 description="API for task submission and status checking"
                                 )

        # POST method to submit a new task
        submit_task_integration = apigateway.LambdaIntegration(self.building_clash_docker_lambda)
        api.root.add_resource("detect-clash").add_method("POST", submit_task_integration)

        # Output the API endpoint URL
        CfnOutput(self, "ApiUrl", value=api.url)

        self.dynamodb_table = dynamodb.Table(
            self, "BuildingClashResults",
            partition_key=dynamodb.Attribute(name="task_id", type=dynamodb.AttributeType.STRING),
            table_name="BuildingClashResults",
            #removal_policy=RemovalPolicy.DESTROY  # only for dev/testing
            )
        # Grant permissions to both lambdas
        self.dynamodb_table.grant_read_write_data(self.handle_post_sqs_lambda_fn)
        self.dynamodb_table.grant_read_write_data(self.building_clash_docker_lambda)


