# Code-to-BRD AI Agent

An AI-powered system that automatically extracts functional intent from codebases and generates Business Requirement Documents (BRDs), use cases, and test cases using AWS services.

## Architecture Overview

This system uses AWS services to provide:
- **Functional Extraction**: Analyze code to extract key functional intent and behaviors
- **BRD Generation**: Create business requirement documents in stakeholder-friendly format
- **Use Case Synthesis**: Generate detailed use cases and business scenarios
- **Test Suite Creation**: Generate unit, functional, and edge case test scenarios
- **Traceability**: Maintain links between code, BRDs, scenarios, and test cases

## AWS Services Used

- **AWS Bedrock**: LLM capabilities for natural language processing and generation
- **Amazon SageMaker**: Custom ML models and processing pipelines for code analysis
- **AWS Lambda**: Serverless compute for orchestration and API handling
- **Amazon API Gateway**: REST API endpoints
- **Amazon S3**: Storage for codebases and generated artifacts
- **Amazon DynamoDB**: Metadata storage and traceability relationships
- **AWS Step Functions**: Workflow orchestration
- **Amazon EventBridge**: Event-driven architecture
- **Amazon CloudWatch**: Monitoring and KPI tracking

## Project Structure

```
code-to-brd-system/
├── infrastructure/          # Infrastructure as Code
├── src/                    # Source code
│   ├── lambda/            # Lambda functions
│   ├── sagemaker/         # SageMaker processing jobs
│   ├── bedrock/           # Bedrock integration modules
│   └── shared/            # Shared utilities and models
├── tests/                 # Test suites
├── docs/                  # Documentation
└── deployment/            # Deployment scripts
```

## Getting Started

1. Deploy the infrastructure using CDK
2. Configure AWS Bedrock access
3. Upload a codebase via the API
4. Retrieve generated BRD, use cases, and test cases

## KPIs and Success Metrics

- **BRD Generation Accuracy**: 80% semantic alignment with reference BRDs
- **Test Case Validity**: 75% of generated tests execute successfully
- **Efficiency**: 70% reduction in time for new gateway integrations
- **Cost Effectiveness**: Deployable within current AWS infrastructure

## Supported Languages

- Python
- JavaScript/TypeScript
- Java (planned)
- C# (planned)
