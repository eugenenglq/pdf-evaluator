# WebSocket API Implementation for Streaming Bedrock Responses

## Problem

The application was attempting to use streaming responses from Amazon Bedrock through API Gateway REST APIs, but standard REST API Gateway doesn't support streaming responses natively.

## Solution: WebSocket API

We've implemented a WebSocket API solution to enable true streaming of Bedrock responses to the frontend. This approach allows bidirectional communication between client and server, enabling real-time streaming of AI-generated content.

### Architecture Overview

1. **API Gateway WebSocket API**: Handles WebSocket connections, routes messages, and integrates with Lambda functions
2. **DynamoDB Connections Table**: Stores active WebSocket connection IDs
3. **Lambda Functions**:
   - `websocket-connection`: Manages WebSocket connections (connect/disconnect/message routing)
   - `websocket-send-message`: Sends messages to clients through the WebSocket API
   - `process-image-bedrock`: Modified to support both REST API and WebSocket streaming

### WebSocket Flow

1. Client connects to WebSocket API endpoint
2. Connection ID is stored in DynamoDB
3. Client sends processImage request through WebSocket
4. websocket-connection Lambda routes request to process-image-bedrock Lambda
5. process-image-bedrock sends streaming responses through websocket-send-message Lambda
6. Client receives real-time chunks as they're generated

### Implementation Details

1. **WebSocket Connection Handler**
   - Handles WebSocket lifecycle events ($connect, $disconnect)
   - Routes incoming messages based on action field
   - Stores connection IDs in DynamoDB for message delivery

2. **Message Sender**
   - Dedicated Lambda for sending messages to connected clients
   - Uses API Gateway Management API to post to connections

3. **Updated Bedrock Processing**
   - Supports dual-mode operation (WebSocket or REST API)
   - For WebSocket requests, streams chunks as they're generated
   - For REST API requests, returns complete response

4. **Frontend WebSocket Client**
   - Manages WebSocket connections with automatic reconnect
   - Appends chunks to result in real-time
   - Falls back to REST API if WebSocket is unavailable

### Benefits

1. **Real-time Feedback**: Users see AI-generated content immediately as it's produced
2. **Improved User Experience**: Progressive rendering feels more responsive
3. **Efficient Resource Usage**: No need to wait for the entire response to be generated
4. **Bidirectional Communication**: Enables future enhancements like cancellation or refinement

### Deployment Instructions

1. Merge the template updates into the main SAM template
2. Deploy the updated stack using SAM CLI
3. Update frontend environment variables with the WebSocket endpoint URL
4. Test both WebSocket streaming and REST API fallback functionality