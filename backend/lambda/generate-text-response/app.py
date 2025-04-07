import os
import json
import boto3
import websocket
from aws_lambda_powertools import Logger
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
from langchain_aws.chat_models import ChatBedrock
from langchain_aws.embeddings import BedrockEmbeddings
from langchain.retrievers.bedrock import AmazonKnowledgeBasesRetriever
from langchain.llms.bedrock import Bedrock
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser

MODEL_ID = os.environ["MODEL_ID"]
EMBEDDING_MODEL_ID = os.environ["EMBEDDING_MODEL_ID"]
lambda_client = boto3.client('lambda')
s3 = boto3.client("s3")
logger = Logger()

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
        websocket.send_websocket_message(connection_id, domain_name, message)
        return True
    except Exception as e:
        logger.error(f"Error sending WebSocket message: {str(e)}")
        return False
    

def bedrock_chain(bedrock_kb_id, connection_id, domain_name, prompt_template, human_input, bedrock_runtime):
    print('prompt_template', prompt_template)
    print('human_input', human_input)

    # Initialize boto3 client for Bedrock Runtime and Knowledge Bases
    bedrock_runtime_client = boto3.client('bedrock-runtime', region_name="us-west-2")
    bedrock_kb_client = boto3.client('bedrock-agent-runtime')

    # Get context from Knowledge Base using boto3
    kb_response = bedrock_kb_client.retrieve(
        knowledgeBaseId=bedrock_kb_id,
        retrievalQuery={
            'text': human_input
        },
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": 1
            }
        }
    )

    # Extract and join the context from the retrieved documents
    context = "\n".join(
        result['content']['text'] 
        for result in kb_response['retrievalResults']
    )

    # Format the prompt with context and question
    # formatted_prompt = prompt_template.format(context=context, question=human_input)

    # # Prepare the request body for Claude 3
    # request_body = {
    #     "anthropic_version": "bedrock-2023-05-31",
    #     "messages": [
    #         {
    #             "role": "user",
    #             "content": formatted_prompt
    #         }
    #     ],
    #     "temperature": 0.0,
    #     "max_tokens": 4096
    # }

    # # Make streaming request to Bedrock Runtime
    # response = bedrock_runtime_client.invoke_model_with_response_stream(
    #     modelId=MODEL_ID,
    #     body=json.dumps(request_body)
    # )

    # Format the prompt with context and question
    formatted_prompt = prompt_template.format(context=context, question=human_input)

    # Prepare the message for Claude 3
    message = {
        "content": [{"text": formatted_prompt}],
        "role": "user"
    }

    response = bedrock_runtime_client.converse_stream(
        modelId=MODEL_ID,
        messages=[message],
        inferenceConfig= {
            'maxTokens': 120000,
            'temperature': 0.0
        }
    )

    

    full_response = ""
    # Process the streaming response
    for event in response['stream']:
        # Handle different event types
        if 'contentBlockDelta' in event:
            if 'delta' in event['contentBlockDelta']:
                delta = event['contentBlockDelta']['delta']
                if 'text' in delta:
                    text_chunk = delta['text']
                    full_response += text_chunk
                    
                    if connection_id:
                        send_websocket_message(
                            connection_id,
                            domain_name,
                            {'chunk': text_chunk, 'done': False}
                        )

    response = bedrock_runtime_client.converse_stream(
    modelId=MODEL_ID,
    messages=[message],
    inferenceConfig={
        'maxTokens': 120000,
        'temperature': 0.0
    }
)

                    
    # full_response = ""
    # # Process the streaming response
    # for event in response['body']:
    #     chunk = json.loads(event['chunk']['bytes'].decode())
    #     if 'completion' in chunk:
    #         text_chunk = chunk['completion']
    #         full_response += text_chunk
            
    #         if connection_id:
    #             send_websocket_message(
    #                 connection_id,
    #                 domain_name,
    #                 {'chunk': text_chunk, 'done': False}
    #             )

                
    # Send final message indicating completion
    send_websocket_message(
        connection_id,
        domain_name,
        {'chunk': '', 'done': True, 'fullResponse': full_response}
    )
    return full_response


def lambda_handler(event, context):
    print(event)
    
    # Check if this is a WebSocket request (has connectionId)
    connection_id = None
    domain_name = None
    
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    connection_id = event.get('connectionId')
    domain_name = event.get('domainName')
    bedrock_kb_id = event.get('bedrockKBID')
    human_input = event.get('prompt')
    prompt_template = event.get('prompt_template')
    
    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-west-2",
    )

    response = bedrock_chain(bedrock_kb_id, connection_id, domain_name, prompt_template, human_input, bedrock_runtime)
    if response:
        print('human_input', human_input)
        print('response', response)
    else:
        raise ValueError(f"Unsupported model ID: {MODEL_ID}")

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(response),
    }