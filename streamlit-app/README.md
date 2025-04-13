# Streamlit Application Deployment Guide

This guide explains how to deploy a Streamlit application on AWS using CloudFormation, ECR, and ECS Fargate.

## Prerequisites

- AWS CLI installed and configured with appropriate credentials
- Docker installed on your local machine
- Git (to clone this repository)
- Your Streamlit application code

## Deployment Steps

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Deploy the CloudFormation Stack
```bash
aws cloudformation create-stack \
  --stack-name pdf-evaluator-stack \
  --template-body file://cfn_template.yaml \
  --capabilities CAPABILITY_IAM
  
```

Wait for the stack creation to complete (approximately 5-10 minutes). You can monitor the progress in the AWS Console or using:

```bash
aws cloudformation describe-stacks --stack-name pdf-evaluator-stack
```

### 3. Get the ECR Repository URL
```bash
export ECR_REPO=$(aws cloudformation describe-stacks \
  --stack-name pdf-evaluator-stack \
  --query 'Stacks[0].Outputs[?ExportName==`streamlit-app-ECRRepository`].OutputValue' \
  --output text)
```

### 4. Authenticate Docker with ECR
```bash
aws ecr get-login-password --region us-west-1 | docker login --username AWS --password-stdin $ECR_REPO
```

### 5. Build and Push Docker Image
Create a Dockerfile in your application directory:

```bash
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]

```

dockerfile
Build and push the image:

```bash
docker build -t streamlit-app .
docker tag streamlit-app:latest $ECR_REPO:latest
docker push $ECR_REPO:latest
```

### 6. Get the Application URL
```bash
aws cloudformation describe-stacks \
  --stack-name pdf-evaluator-stack \
  --query 'Stacks[0].Outputs[?ExportName==`streamlit-app-ALBDNS`].OutputValue' \
  --output text
```

The application will be accessible at http://<ALB_DNS_NAME>

Infrastructure Details
The deployment creates:

VPC with 2 public and 2 private subnets

Internet Gateway and NAT Gateway

Application Load Balancer

ECS Cluster with Fargate

ECR Repository

Security Groups

CloudWatch Log Group

Monitoring and Logs
Access container logs in CloudWatch:

Log Group: /ecs/streamlit-app

Each task will have its own log stream

## Cleanup
To delete all resources:

# Delete all images from ECR repository first
aws ecr batch-delete-images \
  --repository-name streamlit-app-repo \
  --image-ids imageTag=latest

# Delete the CloudFormation stack
aws cloudformation delete-stack --stack-name pdf-evaluator-stack
