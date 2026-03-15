#!/bin/bash

# Deployment script for Code-to-BRD System
# This script deploys the complete infrastructure using AWS CDK

set -e

echo "🚀 Starting Code-to-BRD System Deployment"

# Check if AWS CLI is installed and configured
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first."
    exit 1
fi

# Check if CDK is installed
if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK is not installed. Installing..."
    npm install -g aws-cdk
fi

# Check AWS credentials
echo "🔐 Checking AWS credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Please run 'aws configure' first."
    exit 1
fi

# Get AWS account and region
AWS_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)
echo "📍 AWS Account: $AWS_ACCOUNT"
echo "📍 AWS Region: $AWS_REGION"

# Check if Bedrock is available in the region
echo "🤖 Checking AWS Bedrock availability..."
if ! aws bedrock list-foundation-models --region $AWS_REGION &> /dev/null; then
    echo "❌ AWS Bedrock is not available in region $AWS_REGION"
    echo "Please choose a region where Bedrock is available (e.g., us-east-1, us-west-2)"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd infrastructure/cdk
pip install -r requirements.txt

# Bootstrap CDK if needed
echo "🔧 Bootstrapping CDK..."
cdk bootstrap aws://$AWS_ACCOUNT/$AWS_REGION

# Deploy the stack
echo "🏗️ Deploying Code-to-BRD infrastructure..."
cdk deploy --require-approval never

# Get stack outputs
echo "📋 Getting deployment outputs..."
API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name CodeToBrdStack --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' --output text)
CODEBASE_BUCKET=$(aws cloudformation describe-stacks --stack-name CodeToBrdStack --query 'Stacks[0].Outputs[?OutputKey==`CodebaseBucketName`].OutputValue' --output text)
ARTIFACTS_BUCKET=$(aws cloudformation describe-stacks --stack-name CodeToBrdStack --query 'Stacks[0].Outputs[?OutputKey==`ArtifactsBucketName`].OutputValue' --output text)

echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Deployment Summary:"
echo "  API Endpoint: $API_ENDPOINT"
echo "  Codebase Bucket: $CODEBASE_BUCKET"
echo "  Artifacts Bucket: $ARTIFACTS_BUCKET"
echo ""
echo "🧪 Testing the deployment..."

# Test the API endpoint
if curl -s "$API_ENDPOINT/projects" > /dev/null; then
    echo "✅ API endpoint is responding"
else
    echo "⚠️ API endpoint test failed - this might be normal if no projects exist yet"
fi

echo ""
echo "🎉 Code-to-BRD System is ready!"
echo ""
echo "📖 Next steps:"
echo "  1. Upload a codebase using: POST $API_ENDPOINT/upload"
echo "  2. Check project status: GET $API_ENDPOINT/projects"
echo "  3. Retrieve generated artifacts: GET $API_ENDPOINT/projects/{project_id}/brd"
echo ""
echo "📚 For more information, see the documentation in the docs/ folder"
