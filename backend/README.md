# Bedrock File Processing API

This project implements an API Gateway and Lambda function that can process files with Amazon Bedrock. The API accepts a base64-encoded file and a prompt, invokes Bedrock with streaming responses, and returns the generated content.

## Architecture

- **API Gateway**: Exposes a REST API endpoint that accepts POST requests with base64-encoded files and prompts
- **Lambda Function**: Processes the requests, decodes the files, and invokes Amazon Bedrock
- **Amazon Bedrock**: Processes the file content and prompt using the Claude 3 Sonnet model

## Prerequisites

- AWS CLI configured with appropriate credentials
- AWS SAM CLI installed
- Python 3.9+

## Deployment

1. Build the SAM application:
```bash
cd backend
sam build
```

2. Deploy the application:
```bash
sam deploy --guided
```
For subsequent deployments, you can simply use:
sam deploy
