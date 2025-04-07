import json
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('healthcare-demo-prompts')
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
    
    try:
        http_method = event['httpMethod']
        
        if http_method == 'POST':
            # Save new prompt
            body = json.loads(event['body'])
            item = {
                'demo': body['demo'],
                'title': body['title'],
                'prompt': body['prompt']
            }

            if 'prompt_template' in body:
                item['prompt_template'] = body['prompt_template']
                
            table.put_item(Item=item)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'message': 'Prompt saved successfully'})
            }
            
        elif http_method == 'GET':
            # Get prompts for a demo
            demo = event['queryStringParameters'].get('demo')
            response = table.query(
                KeyConditionExpression=Key('demo').eq(demo)
            )
            items = response['Items']
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(items)
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'headers': headers,
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }