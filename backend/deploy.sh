#!/bin/bash

# Deployment script for Bedrock File Processing API
# Usage: ./deploy.sh <stack-name> <s3-bucket-name>

# Check if required parameters are provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <stack-name> <s3-bucket-name>"
    exit 1
fi

STACK_NAME=$1
S3_BUCKET=$2

echo "Starting deployment of $STACK_NAME using bucket $S3_BUCKET..."

# Build the application
echo "Building application..."
sam build || { echo "Build failed"; exit 1; }

# Deploy the application
echo "Deploying application..."
sam deploy \
    --stack-name $STACK_NAME \
    --s3-bucket $S3_BUCKET \
    --capabilities CAPABILITY_IAM \
    --no-confirm-changeset \
    --no-fail-on-empty-changeset || { echo "Deployment failed"; exit 1; }

# Get the API Gateway URL
API_URL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='BedrockApiEndpoint'].OutputValue" --output text)

echo ""
echo "Deployment completed successfully!"
echo "API Endpoint: $API_URL"
echo ""
echo "Example usage:"
echo "curl -X POST $API_URL -H 'Content-Type: application/json' -d '{\"file\": \"YmFzZTY0IHN0cmluZyBvZiBmaWxlIGNvbnRlbnQ=\", \"prompt\": \"Your prompt here\"}'"