# System Architecture

## High-Level Architecture

The Code-to-BRD system follows a microservices architecture using AWS serverless services:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Upload   │───▶│   API Gateway   │───▶│   S3 Bucket     │
│   (Codebase)    │    │                 │    │   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Step Functions  │
                       │ (Orchestration) │
                       └─────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │   SageMaker     │ │   AWS Bedrock   │ │   Lambda        │
    │ (Code Analysis) │ │ (BRD/Test Gen)  │ │ (Traceability)  │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
                │               │               │
                └───────────────┼───────────────┘
                                ▼
                       ┌─────────────────┐
                       │   DynamoDB      │
                       │ (Metadata &     │
                       │  Traceability)  │
                       └─────────────────┘
```

## Component Details

### 1. Input Processing
- **S3 Bucket**: Stores uploaded codebases
- **Lambda (code-upload)**: Validates and processes uploads
- **API Gateway**: REST endpoints for upload and retrieval

### 2. Code Analysis Engine
- **SageMaker Processing Job**: Static code analysis using AST parsing
- **Custom Containers**: Language-specific parsers
- **Bedrock Integration**: Semantic analysis of code structure

### 3. BRD Generation Pipeline
- **Bedrock (Claude 3.5 Sonnet)**: Natural language generation
- **Prompt Engineering**: Consistent BRD format templates
- **Template System**: Customizable output formats

### 4. Use Case Synthesis
- **Bedrock Models**: Scenario and narrative generation
- **Integration Layer**: Connects code analysis with business scenarios
- **Validation**: Ensures use cases align with extracted functionality

### 5. Test Case Generation
- **Multiple Bedrock Models**: Different test types (unit, functional, edge)
- **Code Coverage Analysis**: Ensures comprehensive test coverage
- **Framework Integration**: Generates tests for popular frameworks

### 6. Traceability System
- **DynamoDB**: Stores relationships between components
- **Graph Concepts**: Links code → BRD → use cases → tests
- **Query API**: Retrieve related components

## Data Flow

1. **Upload**: User uploads codebase to S3 via API Gateway
2. **Trigger**: S3 event triggers Step Functions workflow
3. **Analysis**: SageMaker processes code for functional extraction
4. **Generation**: Bedrock generates BRD, use cases, and test cases
5. **Storage**: Results stored in S3, metadata in DynamoDB
6. **Retrieval**: API endpoints provide access to generated artifacts

## Security & Compliance

- **IAM Roles**: Least privilege access for all services
- **VPC**: Secure network configuration
- **Encryption**: Data encrypted at rest and in transit
- **Audit Logging**: CloudTrail for all API calls
- **Data Privacy**: No sensitive data stored in logs

## Scalability & Performance

- **Auto-scaling**: Lambda and SageMaker auto-scale based on demand
- **Caching**: CloudFront for API responses
- **Batch Processing**: Support for large codebases
- **Parallel Processing**: Multiple analysis jobs for efficiency

## Monitoring & KPIs

- **CloudWatch**: Metrics, logs, and alarms
- **Custom Metrics**: BRD accuracy, test validity, processing time
- **Cost Tracking**: Per-operation cost analysis
- **Success Rates**: Processing success/failure tracking
