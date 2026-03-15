# Code-to-BRD System Usage Guide

This guide provides comprehensive instructions for using the Code-to-BRD AI Agent system.

## Table of Contents

1. [Getting Started](#getting-started)
2. [API Reference](#api-reference)
3. [Uploading Codebases](#uploading-codebases)
4. [Retrieving Generated Artifacts](#retrieving-generated-artifacts)
5. [Monitoring and KPIs](#monitoring-and-kpis)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.11+ (for local testing)
- Node.js (for CDK deployment)

### Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd code-to-brd-system
   ```

2. **Deploy the infrastructure**
   ```bash
   ./deployment/deploy.sh
   ```

3. **Test the deployment**
   ```bash
   python deployment/test-deployment.py <API_ENDPOINT>
   ```

### Configuration

The system uses the following environment variables:
- `CODEBASE_BUCKET`: S3 bucket for codebase storage
- `ARTIFACTS_BUCKET`: S3 bucket for generated artifacts
- `METADATA_TABLE`: DynamoDB table for metadata
- `STATE_MACHINE_ARN`: Step Functions state machine ARN

## API Reference

### Base URL
```
https://<api-gateway-id>.execute-api.<region>.amazonaws.com/prod
```

### Authentication
Currently, the API is open. In production, implement proper authentication using AWS Cognito or API keys.

### Endpoints

#### 1. Upload Codebase
**POST** `/upload`

Upload a codebase for analysis.

**Request Body:**
```json
{
  "body": "base64_encoded_zip_content",
  "filename": "my-codebase.zip",
  "content_type": "application/zip"
}
```

**Response:**
```json
{
  "project_id": "uuid",
  "execution_arn": "arn:aws:states:...",
  "status": "processing_started",
  "message": "Codebase uploaded successfully and analysis started"
}
```

#### 2. List Projects
**GET** `/projects`

Get a list of all projects.

**Response:**
```json
{
  "projects": [
    {
      "project_id": "uuid",
      "filename": "my-codebase.zip",
      "created_at": "2024-01-01T00:00:00Z",
      "status": "completed",
      "languages": ["python", "javascript"],
      "file_count": 42
    }
  ],
  "total": 1
}
```

#### 3. Get Project Details
**GET** `/projects/{project_id}`

Get detailed information about a specific project.

**Response:**
```json
{
  "project_id": "uuid",
  "filename": "my-codebase.zip",
  "created_at": "2024-01-01T00:00:00Z",
  "status": "completed",
  "languages": ["python", "javascript"],
  "file_count": 42,
  "total_size": 1024000,
  "s3_key": "projects/uuid/codebase/",
  "components": {
    "code_analysis": {
      "status": "completed",
      "created_at": "2024-01-01T00:01:00Z",
      "has_result": true
    },
    "brd_generation": {
      "status": "completed",
      "created_at": "2024-01-01T00:02:00Z",
      "has_result": true
    }
  }
}
```

#### 4. Get BRD
**GET** `/projects/{project_id}/brd`

Get the generated Business Requirement Document.

**Response:**
```json
{
  "project_id": "uuid",
  "brd_content": "# Business Requirement Document\n\n## Executive Summary\n...",
  "sections": {
    "executive_summary": "...",
    "functional_requirements": "..."
  },
  "generation_timestamp": "2024-01-01T00:02:00Z",
  "download_url": "https://s3.amazonaws.com/..."
}
```

#### 5. Get Use Cases
**GET** `/projects/{project_id}/usecases`

Get the generated use cases and scenarios.

**Response:**
```json
{
  "project_id": "uuid",
  "usecase_content": "# Use Cases and Business Scenarios\n\n## Primary Use Cases\n...",
  "scenarios": [
    {
      "title": "UC-001: Process Order",
      "content": ["Primary Actor: Customer", "Goal: Place an order", "..."]
    }
  ],
  "generation_timestamp": "2024-01-01T00:03:00Z",
  "download_url": "https://s3.amazonaws.com/..."
}
```

#### 6. Get Test Cases
**GET** `/projects/{project_id}/tests`

Get the generated test cases.

**Response:**
```json
{
  "project_id": "uuid",
  "unit_tests": [
    {
      "function": "calculate_total",
      "file": "order_processor.py",
      "test_content": "def test_calculate_total_happy_path():..."
    }
  ],
  "functional_tests": [
    {
      "endpoint": "/api/orders",
      "method": "POST",
      "test_content": "def test_create_order_valid():..."
    }
  ],
  "edge_case_tests": [
    {
      "test_content": "def test_boundary_value_maximum_input():..."
    }
  ],
  "total_tests": 15,
  "generation_timestamp": "2024-01-01T00:04:00Z",
  "download_url": "https://s3.amazonaws.com/..."
}
```

#### 7. Get Traceability Matrix
**GET** `/projects/{project_id}/traceability`

Get the traceability matrix linking components.

**Response:**
```json
{
  "project_id": "uuid",
  "traceability_matrix": {
    "brd_to_usecases": ["BRD Section 1 -> Use Case 1"],
    "usecases_to_tests": ["Use Case 1 -> Functional Test 1"],
    "brd_to_tests": ["BRD Requirement 1 -> Test Case 1"]
  },
  "total_links": 12,
  "creation_timestamp": "2024-01-01T00:05:00Z"
}
```

## Uploading Codebases

### Supported Formats

- **ZIP files**: Most common format
- **TAR.GZ files**: Compressed tar archives
- **TAR files**: Uncompressed tar archives
- **Single files**: Individual source files

### Supported Languages

- Python (.py)
- JavaScript (.js)
- TypeScript (.ts, .tsx)
- Java (.java)
- C# (.cs)
- C++ (.cpp, .cc, .cxx)
- C (.c)
- Go (.go)
- Rust (.rs)
- PHP (.php)
- Ruby (.rb)

### Upload Process

1. **Prepare your codebase**
   - Ensure all source files are included
   - Remove build artifacts and dependencies (node_modules, __pycache__, etc.)
   - Include configuration files if relevant

2. **Create archive**
   ```bash
   zip -r my-codebase.zip src/ config/ README.md
   ```

3. **Encode to base64**
   ```python
   import base64
   
   with open('my-codebase.zip', 'rb') as f:
       content = base64.b64encode(f.read()).decode('utf-8')
   ```

4. **Upload via API**
   ```python
   import requests
   
   payload = {
       'body': content,
       'filename': 'my-codebase.zip',
       'content_type': 'application/zip'
   }
   
   response = requests.post(f'{api_endpoint}/upload', json=payload)
   project_id = response.json()['project_id']
   ```

## Retrieving Generated Artifacts

### Processing Status

Projects go through the following states:
1. `processing` - Initial upload and analysis
2. `code_analysis` - Analyzing code structure
3. `generation` - Generating BRD, use cases, and tests
4. `traceability` - Creating traceability matrix
5. `completed` - All processing finished
6. `failed` - Processing encountered an error

### Polling for Completion

```python
import time
import requests

def wait_for_completion(api_endpoint, project_id, timeout=300):
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = requests.get(f'{api_endpoint}/projects/{project_id}')
        status = response.json()['status']
        
        if status == 'completed':
            return True
        elif status == 'failed':
            return False
        
        time.sleep(10)  # Wait 10 seconds
    
    return False  # Timeout
```

### Downloading Artifacts

All generated artifacts are available as downloadable files:

```python
# Get BRD with download URL
brd_response = requests.get(f'{api_endpoint}/projects/{project_id}/brd')
download_url = brd_response.json()['download_url']

# Download the file
brd_file = requests.get(download_url)
with open('generated_brd.md', 'wb') as f:
    f.write(brd_file.content)
```

## Monitoring and KPIs

### Key Performance Indicators

The system tracks the following KPIs:

1. **BRD Generation Accuracy**: 80% semantic alignment target
2. **Test Case Validity**: 75% of tests execute successfully
3. **Processing Efficiency**: 70% reduction in time vs manual
4. **Success Rate**: 95% successful processing target
5. **Average Processing Time**: 5 minutes target
6. **Cost per Operation**: $5 target

### Accessing Metrics

```python
from src.shared.monitoring import KPITracker

tracker = KPITracker()
dashboard_data = tracker.get_kpi_dashboard_data(days=30)
report = tracker.generate_kpi_report(days=30)
```

### CloudWatch Metrics

The system publishes metrics to CloudWatch under the namespace `CodeToBRD/Projects`:

- `ProcessingTime`: Time taken to process projects
- `FileCount`: Number of files in projects
- `LanguageCount`: Number of programming languages
- `BRDQualityScore`: Quality score of generated BRDs
- `TestCount`: Number of generated test cases
- `UseCaseCount`: Number of generated use cases

## Best Practices

### Codebase Preparation

1. **Clean your codebase**
   - Remove build artifacts
   - Remove dependencies (node_modules, venv, etc.)
   - Include only source code and configuration

2. **Include documentation**
   - README files
   - API documentation
   - Configuration examples

3. **Organize structure**
   - Use clear directory structure
   - Include relevant configuration files
   - Maintain consistent naming conventions

### API Usage

1. **Handle errors gracefully**
   ```python
   try:
       response = requests.post(f'{api_endpoint}/upload', json=payload)
       response.raise_for_status()
   except requests.exceptions.HTTPError as e:
       print(f"Upload failed: {e}")
   ```

2. **Implement retry logic**
   ```python
   import time
   
   def upload_with_retry(api_endpoint, payload, max_retries=3):
       for attempt in range(max_retries):
           try:
               response = requests.post(f'{api_endpoint}/upload', json=payload)
               response.raise_for_status()
               return response.json()
           except requests.exceptions.RequestException as e:
               if attempt == max_retries - 1:
                   raise
               time.sleep(2 ** attempt)  # Exponential backoff
   ```

3. **Monitor processing status**
   - Always check project status before retrieving artifacts
   - Implement timeout handling
   - Log processing times for optimization

### Generated Artifacts

1. **Review generated content**
   - BRDs may need business context refinement
   - Use cases should be validated with stakeholders
   - Test cases should be reviewed for completeness

2. **Customize templates**
   - Modify prompts in `src/bedrock/prompts/` for specific needs
   - Adjust quality thresholds in KPI tracker
   - Customize output formats as needed

## Troubleshooting

### Common Issues

#### 1. Upload Fails
**Symptoms**: 400/500 error on upload
**Solutions**:
- Check file size (max 50MB recommended)
- Verify base64 encoding
- Ensure proper content-type header

#### 2. Processing Stuck
**Symptoms**: Project status remains "processing" for extended time
**Solutions**:
- Check Step Functions execution logs
- Verify Bedrock service availability
- Check Lambda function logs

#### 3. Poor Quality Output
**Symptoms**: Generated BRD/usecases/tests are low quality
**Solutions**:
- Ensure codebase has good documentation
- Check for sufficient business logic functions
- Verify API endpoints are properly defined

#### 4. Missing Components
**Symptoms**: Some generated components are missing
**Solutions**:
- Check DynamoDB for component status
- Verify all Lambda functions executed successfully
- Check for errors in Step Functions execution

### Debugging Steps

1. **Check CloudWatch Logs**
   ```bash
   aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/code-to-brd"
   ```

2. **Check Step Functions Execution**
   ```bash
   aws stepfunctions list-executions --state-machine-arn <state-machine-arn>
   ```

3. **Check DynamoDB Records**
   ```bash
   aws dynamodb scan --table-name code-to-brd-metadata --filter-expression "project_id = :pid" --expression-attribute-values '{":pid":{"S":"<project-id>"}}'
   ```

### Getting Help

1. **Check the logs**: All components log to CloudWatch
2. **Review the architecture**: See `docs/architecture.md`
3. **Test with sample codebase**: Use the test deployment script
4. **Check AWS service status**: Ensure all services are operational

### Performance Optimization

1. **Large codebases**: Consider splitting into smaller projects
2. **Frequent uploads**: Implement caching for repeated analysis
3. **Cost optimization**: Monitor Bedrock usage and optimize prompts
4. **Processing time**: Consider parallel processing for large projects

## Support

For additional support:
- Review the architecture documentation
- Check AWS CloudWatch logs
- Use the test deployment script for validation
- Monitor KPI dashboard for system health
