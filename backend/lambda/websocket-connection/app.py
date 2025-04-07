import json
import logging
import boto3
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
connections_table = dynamodb.Table(os.environ.get('CONNECTIONS_TABLE_NAME'))

def lambda_handler(event, context):
    """
    Lambda function to handle WebSocket API connect/disconnect events
    """
    connection_id = event.get('requestContext', {}).get('connectionId')
    route_key = event.get('requestContext', {}).get('routeKey')
    
    logger.info(f"Received {route_key} event from {connection_id}")
    
    if not connection_id:
        return {'statusCode': 400, 'body': 'Missing connectionId'}
    
    # Handle different route types
    if route_key == '$connect':
        # Store connection ID in DynamoDB
        try:
            connections_table.put_item(
                Item={
                    'connectionId': connection_id,
                    'timestamp': int(event.get('requestContext', {}).get('requestTime', 0))
                }
            )
            return {'statusCode': 200, 'body': 'Connected'}
        except Exception as e:
            logger.error(f"Error storing connection: {str(e)}")
            return {'statusCode': 500, 'body': 'Failed to connect'}
            
    elif route_key == '$disconnect':
        # Remove connection ID from DynamoDB
        try:
            connections_table.delete_item(
                Key={
                    'connectionId': connection_id
                }
            )
            return {'statusCode': 200, 'body': 'Disconnected'}
        except Exception as e:
            logger.error(f"Error removing connection: {str(e)}")
            return {'statusCode': 500, 'body': 'Failed to disconnect'}
            
    elif route_key == 'processImage':
        # Process the message - forward to process-image-bedrock Lambda
        try:
            request_body = json.loads(event.get('body', '{}'))
            lambda_client = boto3.client('lambda')
            
            # Add WebSocket connection information to the request
            request_body['connectionId'] = connection_id
            request_body['domainName'] = event['requestContext']['domainName']
            request_body['stage'] = event['requestContext']['stage']
            
            # Invoke the process-image-bedrock Lambda asynchronously
            lambda_client.invoke(
                FunctionName=os.environ.get('PROCESS_IMAGE_FUNCTION'),
                InvocationType='Event',  # Asynchronous invocation
                Payload=json.dumps(request_body)
            )
            
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Processing started'})
            }
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
    
    # Default response for unsupported routes
    return {
        'statusCode': 400,
        'body': json.dumps({'error': 'Unsupported route'})
    }