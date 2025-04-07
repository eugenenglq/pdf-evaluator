import json
import logging
import base64
import boto3
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
lambda_client = boto3.client('lambda')
BUCKET_NAME = os.environ.get('BUCKET_NAME')
s3_client = boto3.client('s3')

headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def lambda_handler(event, context):
    
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    request_body = json.loads(event['body'])

    try:
        payload = {
            'connectionId': request_body.get('connectionId'),
            'domainName': request_body.get('domainName'),
            'bedrockKBID': request_body.get('bedrockKBID'),
            'prompt': request_body.get('prompt'),
            'prompt_template': request_body.get('prompt_template')
        }
        
        lambda_client.invoke(
            FunctionName=os.environ.get('GENERATE_TEXT_RESPONSE_FUNCTION'),
            InvocationType='Event',
            Payload=json.dumps(payload)
        )
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'ok'})
        }
    
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'An unexpected error occurred: {str(e)}'})
        }