# Frontend Deployment Guide

## Prerequisites
- AWS CLI installed and configured with appropriate credentials
- Node.js and npm installed (for building frontend assets)

## Infrastructure Deployment

### 1. Deploy CloudFormation Stack
The frontend infrastructure is defined in `cfn_template.yaml`. This template creates:
- S3 bucket for hosting frontend files
- CloudFront distribution for content delivery
- Required security configurations and permissions

Deploy the stack using AWS CLI:
```bash
# Deploy the stack
aws cloudformation create-stack \
  --stack-name <YOUR STACK NAME> \
  --template-body file://cfn_template.yaml

# Wait for stack creation to complete
aws cloudformation wait stack-create-complete \
  --stack-name <YOUR STACK NAME>
```

### 2. Get Deployment Information
Retrieve the S3 bucket name and CloudFront distribution ID:

#### Get stack outputs
```bash
aws cloudformation describe-stacks \
  --stack-name <YOUR STACK NAME> \
  --query 'Stacks[0].Outputs'
```

### 3. Build and Deploy Frontend Files
Build your frontend application:

```bash
npm install
npm run build
```

#### Upload built files to S3:

```bash
aws s3 sync build/ s3://<YOUR STACK NAME>-frontend
```

#### Create CloudFront invalidation to refresh content :
```bash
aws cloudfront create-invalidation \
  --distribution-id <REPLACE WITH YOUR CLOUDFRONT DISTRIBUTION ID, REFER TO STEP 2> \
  --paths "/*"
```

### 4. Access Your Website
Your website will be available at the CloudFront domain name. You can get it using:

```bash
aws cloudformation describe-stacks \
  --stack-name <YOUR STACK NAME> \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDomainName`].OutputValue' \
  --output text
```

## Updating the Website
To update your website content:

Build your changes:
```bash
npm run build
```

Upload new files:
```bash
aws s3 sync build/ s3://<REPLACE WITH YOUR BUCKET NAME, REFER TO STEP 2>
```

Create CloudFront invalidation:
```bash
aws cloudfront create-invalidation \
  --distribution-id <REPLACE WITH YOUR CLOUDFRONT DISTRIBUTION ID, REFER TO STEP 2> \
  --paths "/*"
```

### Update CloudFormation Stack
When you need to modify the infrastructure, update the stack using:

Create a change set to review changes
```bash
aws cloudformation create-change-set \
  --stack-name <YOUR STACK NAME> \
  --template-body file://cfn_template.yaml \
  --change-set-name change-set
```

Review the proposed changes
```bash
aws cloudformation describe-change-set \
  --stack-name <YOUR STACK NAME> \
  --change-set-name change-set
```

Execute the change set if changes look correct
```bash
aws cloudformation execute-change-set \
  --stack-name <YOUR STACK NAME> \
  --change-set-name change-set
```

Wait for stack update to complete
```bash
aws cloudformation wait stack-update-complete \
  --stack-name <YOUR STACK NAME>
```

## Cleanup
To remove all resources:

```bash
aws cloudformation delete-stack \
  --stack-name <YOUR STACK NAME>
```