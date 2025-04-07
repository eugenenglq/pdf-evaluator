import json
import logging
import boto3
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Lambda function to send a message to a WebSocket client
    """
    connection_id = event.get('connectionId')
    domain_name = event.get('domainName')
    message = event.get('message', {})
    
    logger.info(f"Sending message to connection {connection_id}")
    print(event)
    
    if not connection_id or not domain_name:
        logger.error("Missing required parameters")
        return {'statusCode': 400, 'body': 'Missing required parameters'}
    
    domain_name = domain_name.replace('wss://', '')
    
    # Create API Gateway Management API client
    gateway_api = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=f'https://{domain_name}'
    )
    
    try:
        # Send the message to the connected client
        gateway_api.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(message).encode('utf-8')
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Message sent successfully'})
        }
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }