#!/bin/bash

# Setup API Knowledge System
# Creates necessary AWS resources for API documentation training and enhanced integration detection

set -e

# Configuration
REGION=${AWS_REGION:-us-east-1}
STACK_NAME="api-knowledge-system"
API_KNOWLEDGE_BUCKET="api-knowledge-base-$(date +%s)"
API_DOCS_TABLE="api-documentation"

echo "Setting up API Knowledge System..."
echo "Region: $REGION"
echo "Stack Name: $STACK_NAME"
echo "S3 Bucket: $API_KNOWLEDGE_BUCKET"
echo "DynamoDB Table: $API_DOCS_TABLE"

# Create S3 bucket for API knowledge base
echo "Creating S3 bucket for API knowledge base..."
aws s3 mb s3://$API_KNOWLEDGE_BUCKET --region $REGION

# Create bucket policy for public read access to documentation
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$API_KNOWLEDGE_BUCKET/*"
        }
    ]
}
EOF

aws s3api put-bucket-policy --bucket $API_KNOWLEDGE_BUCKET --policy file://bucket-policy.json
rm bucket-policy.json

# Create DynamoDB table for API documentation
echo "Creating DynamoDB table for API documentation..."
aws dynamodb create-table \
    --table-name $API_DOCS_TABLE \
    --attribute-definitions \
        AttributeName=id,AttributeType=S \
        AttributeName=service,AttributeType=S \
        AttributeName=type,AttributeType=S \
    --key-schema \
        AttributeName=id,KeyType=HASH \
    --global-secondary-indexes \
        IndexName=service-index,KeySchema='[{AttributeName=service,KeyType=HASH},{AttributeName=type,KeyType=RANGE}],Projection={ProjectionType=ALL},ProvisionedThroughput={ReadCapacityUnits=5,WriteCapacityUnits=5}' \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --region $REGION

# Wait for table to be created
echo "Waiting for DynamoDB table to be created..."
aws dynamodb wait table-exists --table-name $API_DOCS_TABLE --region $REGION

# Create CloudFormation stack for additional resources
echo "Creating CloudFormation stack for additional resources..."
cat > api-knowledge-stack.yaml << EOF
AWSTemplateFormatVersion: '2010-09-09'
Description: 'API Knowledge System Infrastructure'

Parameters:
  ApiKnowledgeBucket:
    Type: String
    Default: $API_KNOWLEDGE_BUCKET
    Description: S3 bucket for API knowledge base
  
  ApiDocsTable:
    Type: String
    Default: $API_DOCS_TABLE
    Description: DynamoDB table for API documentation

Resources:
  # Lambda function for API documentation training
  ApiDocTrainerFunction:
    Type: AWS::Lambda::Function
    Properties:
      FunctionName: api-doc-trainer
      Runtime: python3.9
      Handler: train_api_models.lambda_handler
      Code:
        ZipFile: |
          import json
          import boto3
          import os
          from api_doc_trainer import APIDocTrainer
          
          def lambda_handler(event, context):
              trainer = APIDocTrainer()
              services = event.get('services', ['stripe', 'twilio', 'aws'])
              results = trainer.train_on_api_documentation(services)
              return {
                  'statusCode': 200,
                  'body': json.dumps(results)
              }
      Role: !GetAtt ApiDocTrainerRole.Arn
      Environment:
        Variables:
          API_KNOWLEDGE_BUCKET: !Ref ApiKnowledgeBucket
          API_DOCS_TABLE: !Ref ApiDocsTable
      Timeout: 900  # 15 minutes
      MemorySize: 1024

  # IAM role for API documentation trainer
  ApiDocTrainerRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: ApiKnowledgeAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:PutObject
                  - s3:DeleteObject
                  - s3:ListBucket
                Resource:
                  - !Sub 'arn:aws:s3:::\${ApiKnowledgeBucket}'
                  - !Sub 'arn:aws:s3:::\${ApiKnowledgeBucket}/*'
              - Effect: Allow
                Action:
                  - dynamodb:GetItem
                  - dynamodb:PutItem
                  - dynamodb:Query
                  - dynamodb:Scan
                  - dynamodb:UpdateItem
                  - dynamodb:DeleteItem
                Resource:
                  - !Sub 'arn:aws:dynamodb:\${AWS::Region}:\${AWS::AccountId}:table/\${ApiDocsTable}'
                  - !Sub 'arn:aws:dynamodb:\${AWS::Region}:\${AWS::AccountId}:table/\${ApiDocsTable}/index/*'
              - Effect: Allow
                Action:
                  - bedrock:InvokeModel
                Resource: '*'

  # EventBridge rule for scheduled training
  TrainingSchedule:
    Type: AWS::Events::Rule
    Properties:
      Description: 'Schedule API documentation training'
      ScheduleExpression: 'rate(7 days)'  # Weekly training
      State: ENABLED
      Targets:
        - Arn: !GetAtt ApiDocTrainerFunction.Arn
          Id: ApiDocTrainerTarget
          Input: '{"services": ["stripe", "twilio", "aws", "sendgrid", "google", "microsoft", "slack", "github", "paypal", "shopify"]}'

  # Permission for EventBridge to invoke Lambda
  TrainingSchedulePermission:
    Type: AWS::Lambda::Permission
    Properties:
      FunctionName: !Ref ApiDocTrainerFunction
      Action: lambda:InvokeFunction
      Principal: events.amazonaws.com
      SourceArn: !GetAtt TrainingSchedule.Arn

Outputs:
  ApiKnowledgeBucket:
    Description: 'S3 bucket for API knowledge base'
    Value: !Ref ApiKnowledgeBucket
    Export:
      Name: !Sub '\${AWS::StackName}-ApiKnowledgeBucket'
  
  ApiDocsTable:
    Description: 'DynamoDB table for API documentation'
    Value: !Ref ApiDocsTable
    Export:
      Name: !Sub '\${AWS::StackName}-ApiDocsTable'
  
  ApiDocTrainerFunction:
    Description: 'Lambda function for API documentation training'
    Value: !Ref ApiDocTrainerFunction
    Export:
      Name: !Sub '\${AWS::StackName}-ApiDocTrainerFunction'
EOF

aws cloudformation create-stack \
    --stack-name $STACK_NAME \
    --template-body file://api-knowledge-stack.yaml \
    --parameters \
        ParameterKey=ApiKnowledgeBucket,ParameterValue=$API_KNOWLEDGE_BUCKET \
        ParameterKey=ApiDocsTable,ParameterValue=$API_DOCS_TABLE \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $REGION

# Wait for stack creation
echo "Waiting for CloudFormation stack to be created..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION

# Clean up temporary files
rm api-knowledge-stack.yaml

# Create environment file for local development
cat > .env.api-knowledge << EOF
# API Knowledge System Configuration
API_KNOWLEDGE_BUCKET=$API_KNOWLEDGE_BUCKET
API_DOCS_TABLE=$API_DOCS_TABLE
AWS_REGION=$REGION

# Training Configuration
TRAINING_SERVICES=stripe,twilio,aws,sendgrid,google,microsoft,slack,github,paypal,shopify
TRAINING_SCHEDULE=weekly
EOF

echo ""
echo "✅ API Knowledge System setup completed!"
echo ""
echo "Resources created:"
echo "  - S3 Bucket: $API_KNOWLEDGE_BUCKET"
echo "  - DynamoDB Table: $API_DOCS_TABLE"
echo "  - CloudFormation Stack: $STACK_NAME"
echo "  - Lambda Function: api-doc-trainer"
echo "  - EventBridge Rule: Weekly training schedule"
echo ""
echo "Next steps:"
echo "  1. Run initial training: python src/shared/api-knowledge/train_api_models.py --all"
echo "  2. Update your Lambda functions to use the enhanced integration detector"
echo "  3. Test the enhanced integration detection"
echo ""
echo "Environment variables saved to: .env.api-knowledge"
echo ""
echo "To start training immediately:"
echo "  aws lambda invoke --function-name api-doc-trainer --payload '{\"services\": [\"stripe\", \"twilio\", \"aws\"]}' response.json"
