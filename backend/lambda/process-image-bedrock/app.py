import json
import logging
import base64
import boto3
import os
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Bedrock client
bedrock_runtime = boto3.client('bedrock-runtime', 'us-west-2')
lambda_client = boto3.client('lambda')
s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']

# Default model to use
MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
}

def send_websocket_message(connection_id, domain_name, message):
    """
    Send a message to a WebSocket client using the websocket-send-message Lambda function
    """
    try:
        payload = {
            'connectionId': connection_id,
            'domainName': domain_name,
            'message': message
        }
        
        lambda_client.invoke(
            FunctionName=os.environ.get('WEBSOCKET_SEND_MESSAGE_FUNCTION'),
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        return True
    except Exception as e:
        logger.error(f"Error sending WebSocket message: {str(e)}")
        return False

def lambda_handler(event, context):
    """
    Lambda function handler that processes API requests containing a base64 encoded file and prompt,
    then invokes Amazon Bedrock with streaming response and returns chunks via WebSocket if used.
    """
    # logger.info("Received event: %s", json.dumps(event)[:1000])
    print(event)
    
    # Check if this is a WebSocket request (has connectionId)
    is_websocket = False
    connection_id = None
    domain_name = None
    
    if 'connectionId' in event:
        is_websocket = True
        connection_id = event.get('connectionId')
        domain_name = event.get('domainName')
        logger.info(f"Processing WebSocket request for connection {connection_id}")
    else:
        logger.info("Processing REST API request")

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }

    try:
        logger.info("Processing incoming request")
        prompt = event.get('prompt')
        
        s3FileKey = event.get('s3FileKey')
        if not s3FileKey:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing s3FileKey'})
            }

        # Download file from S3
        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=s3FileKey
        )
        file_bytes = response['Body'].read()

        doc_message = {
            "role": "user",
            "content": [
                {
                    "document": {
                        "name": "Document 1",
                        "format": "pdf",
                        "source": {
                            "bytes": file_bytes
                        }
                    }
                },
                { "text": "Based on the document, " + prompt }
            ]
        }
        
        # Invoke Bedrock with streaming
        try:
            # Invoke Bedrock with streaming
            response_stream = bedrock_runtime.converse_stream(
                modelId=MODEL_ID,
                messages=[doc_message],
                inferenceConfig={
                    "maxTokens": 2000,
                    "temperature": 0
                },
            )
            
            # Set headers for streaming response
            streaming_headers = headers.copy()
            streaming_headers['Content-Type'] = 'text/event-stream'
            streaming_headers['Cache-Control'] = 'no-cache'
            streaming_headers['Transfer-Encoding'] = 'chunked'
            streaming_headers['X-Content-Type-Options'] = 'nosniff'
            
            # Process the streaming response chunks as they arrive
            if is_websocket:
                print('started 3')
                # For WebSocket requests, send each chunk as it arrives
                full_response = ""

                for chunk in response_stream["stream"]:
                    if "contentBlockDelta" in chunk:
                        text_chunk = chunk["contentBlockDelta"]["delta"]["text"]
                        full_response += text_chunk
                        send_websocket_message(
                                    connection_id,
                                    domain_name,
                                    {'chunk': text_chunk, 'done': False}
                                )
                
                # Send final message indicating completion
                send_websocket_message(
                    connection_id,
                    domain_name,
                    {'chunk': '', 'done': True, 'fullResponse': full_response}
                )
                
                # Return success response (though it's not used by client)
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({'response': full_response}),
                    'isBase64Encoded': False
                }
            else:
                # For REST API requests, collect all chunks and return as a single response
                full_response = ""
                for event in response_stream:
                    if 'chunk' in event:
                        chunk = event['chunk']
                        if 'message' in chunk and 'content' in chunk['message']:
                            content = chunk['message']['content']
                            if content and len(content) > 0 and 'text' in content[0]:
                                text_chunk = content[0]['text']
                                full_response += text_chunk
                
                # Return the complete response (non-streaming)
                return {
                    'statusCode': 200,
                    'headers': headers,
                    'body': json.dumps({'response': full_response}),
                    'isBase64Encoded': False
                }

        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': str(e)})
            }
    
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'An unexpected error occurred: {str(e)}'})
        }