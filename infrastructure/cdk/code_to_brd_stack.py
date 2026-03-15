"""
CDK Stack for Code-to-BRD System
Creates all necessary AWS resources for the AI-powered code analysis system
"""

from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_sagemaker as sagemaker,
    aws_iam as iam,
    aws_logs as logs,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct


class CodeToBrdStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket for codebase storage
        self.codebase_bucket = s3.Bucket(
            self, "CodebaseBucket",
            bucket_name=f"code-to-brd-codebases-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteIncompleteMultipartUploads",
                    abort_incomplete_multipart_upload_after=Duration.days(1)
                )
            ]
        )

        # Create S3 bucket for generated artifacts
        self.artifacts_bucket = s3.Bucket(
            self, "ArtifactsBucket",
            bucket_name=f"code-to-brd-artifacts-{self.account}",
            versioned=True,
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Create DynamoDB table for metadata and traceability
        self.metadata_table = dynamodb.Table(
            self, "MetadataTable",
            table_name="code-to-brd-metadata",
            partition_key=dynamodb.Attribute(
                name="project_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="component_type",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN
        )

        # Add GSI for traceability queries
        self.metadata_table.add_global_secondary_index(
            index_name="component-lookup",
            partition_key=dynamodb.Attribute(
                name="component_type",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            )
        )

        # Create IAM role for Lambda functions
        self.lambda_role = iam.Role(
            self, "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
            inline_policies={
                "CodeToBrdPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:DeleteObject",
                                "s3:ListBucket"
                            ],
                            resources=[
                                self.codebase_bucket.bucket_arn,
                                f"{self.codebase_bucket.bucket_arn}/*",
                                self.artifacts_bucket.bucket_arn,
                                f"{self.artifacts_bucket.bucket_arn}/*"
                            ]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "dynamodb:GetItem",
                                "dynamodb:PutItem",
                                "dynamodb:UpdateItem",
                                "dynamodb:DeleteItem",
                                "dynamodb:Query",
                                "dynamodb:Scan"
                            ],
                            resources=[self.metadata_table.table_arn]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "bedrock:InvokeModel",
                                "bedrock:InvokeModelWithResponseStream"
                            ],
                            resources=["*"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "sagemaker:CreateProcessingJob",
                                "sagemaker:DescribeProcessingJob",
                                "sagemaker:StopProcessingJob"
                            ],
                            resources=["*"]
                        ),
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "states:StartExecution",
                                "states:DescribeExecution",
                                "states:StopExecution"
                            ],
                            resources=["*"]
                        )
                    ]
                )
            }
        )

        # Create Lambda function for code upload processing
        self.code_upload_lambda = lambda_.Function(
            self, "CodeUploadLambda",
            function_name="code-to-brd-upload-processor",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="code_upload.handler",
            code=lambda_.Code.from_asset("../../src/lambda/code-upload"),
            role=self.lambda_role,
            timeout=Duration.minutes(5),
            memory_size=512,
            environment={
                "CODEBASE_BUCKET": self.codebase_bucket.bucket_name,
                "ARTIFACTS_BUCKET": self.artifacts_bucket.bucket_name,
                "METADATA_TABLE": self.metadata_table.table_name
            }
        )

        # Create Lambda function for workflow orchestration
        self.workflow_lambda = lambda_.Function(
            self, "WorkflowLambda",
            function_name="code-to-brd-workflow-orchestrator",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="workflow_orchestrator.handler",
            code=lambda_.Code.from_asset("../../src/lambda/workflow-orchestrator"),
            role=self.lambda_role,
            timeout=Duration.minutes(15),
            memory_size=1024,
            environment={
                "CODEBASE_BUCKET": self.codebase_bucket.bucket_name,
                "ARTIFACTS_BUCKET": self.artifacts_bucket.bucket_name,
                "METADATA_TABLE": self.metadata_table.table_name
            }
        )

        # Create Lambda function for API handlers
        self.api_lambda = lambda_.Function(
            self, "ApiLambda",
            function_name="code-to-brd-api-handler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="api_handler.handler",
            code=lambda_.Code.from_asset("../../src/lambda/api-handlers"),
            role=self.lambda_role,
            timeout=Duration.minutes(2),
            memory_size=256,
            environment={
                "CODEBASE_BUCKET": self.codebase_bucket.bucket_name,
                "ARTIFACTS_BUCKET": self.artifacts_bucket.bucket_name,
                "METADATA_TABLE": self.metadata_table.table_name
            }
        )

        # Create API Gateway
        self.api = apigateway.RestApi(
            self, "CodeToBrdApi",
            rest_api_name="code-to-brd-api",
            description="API for Code-to-BRD system",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )

        # Add API endpoints
        upload_resource = self.api.root.add_resource("upload")
        upload_resource.add_method(
            "POST",
            apigateway.LambdaIntegration(self.code_upload_lambda)
        )

        projects_resource = self.api.root.add_resource("projects")
        projects_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(self.api_lambda)
        )

        project_resource = projects_resource.add_resource("{project_id}")
        project_resource.add_method(
            "GET",
            apigateway.LambdaIntegration(self.api_lambda)
        )

        # Create CloudWatch Log Group for Step Functions
        self.step_functions_log_group = logs.LogGroup(
            self, "StepFunctionsLogGroup",
            log_group_name="/aws/stepfunctions/code-to-brd",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY
        )

        # Create Step Functions state machine
        self.create_step_functions()

        # Create SageMaker processing job role
        self.sagemaker_role = iam.Role(
            self, "SageMakerProcessingRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSageMakerFullAccess")
            ],
            inline_policies={
                "SageMakerProcessingPolicy": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:ListBucket"
                            ],
                            resources=[
                                self.codebase_bucket.bucket_arn,
                                f"{self.codebase_bucket.bucket_arn}/*",
                                self.artifacts_bucket.bucket_arn,
                                f"{self.artifacts_bucket.bucket_arn}/*"
                            ]
                        )
                    ]
                )
            }
        )

        # Outputs
        CfnOutput(
            self, "ApiEndpoint",
            value=self.api.url,
            description="API Gateway endpoint URL"
        )

        CfnOutput(
            self, "CodebaseBucketName",
            value=self.codebase_bucket.bucket_name,
            description="S3 bucket for codebase storage"
        )

        CfnOutput(
            self, "ArtifactsBucketName",
            value=self.artifacts_bucket.bucket_name,
            description="S3 bucket for generated artifacts"
        )

    def create_step_functions(self):
        """Create Step Functions state machine for workflow orchestration"""
        
        # Define the workflow steps
        code_analysis_task = tasks.LambdaInvoke(
            self, "CodeAnalysisTask",
            lambda_function=self.workflow_lambda,
            payload=sfn.TaskInput.from_object({
                "step": "code_analysis",
                "project_id.$": "$.project_id",
                "s3_key.$": "$.s3_key"
            })
        )

        brd_generation_task = tasks.LambdaInvoke(
            self, "BrdGenerationTask",
            lambda_function=self.workflow_lambda,
            payload=sfn.TaskInput.from_object({
                "step": "brd_generation",
                "project_id.$": "$.project_id",
                "analysis_results.$": "$.analysis_results"
            })
        )

        usecase_generation_task = tasks.LambdaInvoke(
            self, "UsecaseGenerationTask",
            lambda_function=self.workflow_lambda,
            payload=sfn.TaskInput.from_object({
                "step": "usecase_generation",
                "project_id.$": "$.project_id",
                "analysis_results.$": "$.analysis_results"
            })
        )

        test_generation_task = tasks.LambdaInvoke(
            self, "TestGenerationTask",
            lambda_function=self.workflow_lambda,
            payload=sfn.TaskInput.from_object({
                "step": "test_generation",
                "project_id.$": "$.project_id",
                "analysis_results.$": "$.analysis_results"
            })
        )

        traceability_task = tasks.LambdaInvoke(
            self, "TraceabilityTask",
            lambda_function=self.workflow_lambda,
            payload=sfn.TaskInput.from_object({
                "step": "traceability",
                "project_id.$": "$.project_id",
                "brd_results.$": "$.brd_results",
                "usecase_results.$": "$.usecase_results",
                "test_results.$": "$.test_results"
            })
        )

        # Create parallel execution for generation tasks
        parallel_generation = sfn.Parallel(
            self, "ParallelGeneration",
            comment="Generate BRD, use cases, and tests in parallel"
        )

        parallel_generation.branch(brd_generation_task)
        parallel_generation.branch(usecase_generation_task)
        parallel_generation.branch(test_generation_task)

        # Define the complete workflow
        definition = (
            code_analysis_task
            .next(parallel_generation)
            .next(traceability_task)
        )

        # Create the state machine
        self.state_machine = sfn.StateMachine(
            self, "CodeToBrdStateMachine",
            state_machine_name="code-to-brd-workflow",
            definition=definition,
            logs=sfn.LogOptions(
                destination=self.step_functions_log_group,
                level=sfn.LogLevel.ALL
            ),
            timeout=Duration.hours(2)
        )

        # Grant permissions to Lambda to start Step Functions
        self.state_machine.grant_start_execution(self.code_upload_lambda)
