// useWebSocket.js
import { useState, useEffect, useCallback, useRef } from 'react';
import WebSocketClient from './websocket-client';

const useWebSocket = (onMessageCallback) => {
  const [websocket, setWebsocket] = useState(null);
  const [connectionId, setConnectionId] = useState(null);
  const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
  const [error, setError] = useState(null);
  
  // Use refs to track initialization and prevent double setup
  const wsClientRef = useRef(null);
  const isInitializedRef = useRef(false);

  const requestConnectionInfo = useCallback((client) => {
    console.log('Sending request for connection details');
    client?.send({
      action: 'getConnectionInfo',
      type: 'connectionRequest',
      message: 'Requesting connection details'
    });
  }, []);

  useEffect(() => {
    // Prevent double initialization
    if (isInitializedRef.current) return;
    isInitializedRef.current = true;

    const setupWebSocket = () => {
      if (wsClientRef.current) return;

      console.log('Initializing WebSocket connection');
      const wsClient = new WebSocketClient(`${process.env.REACT_APP_WS_ENDPOINT}`);

      wsClient.onOpen = () => {
        console.log('WebSocket connection established', wsClient);
        setWebsocket(wsClient);
        setIsWebSocketConnected(true);
        requestConnectionInfo(wsClient);
      };

      wsClient.onMessage = (data) => {
        if (data.connectionId) {
          setConnectionId(data.connectionId);
        }
        onMessageCallback?.(data);
      };

      wsClient.onClose = () => {
        console.log('WebSocket connection closed');
        setIsWebSocketConnected(false);
        setWebsocket(null);
        wsClientRef.current = null;
      };

      wsClient.onError = (error) => {
        console.error('WebSocket error:', error);
        setError(error);
      };

      wsClient.connect();
      wsClientRef.current = wsClient;
    };

    setupWebSocket();

    return () => {
      if (wsClientRef.current) {
        wsClientRef.current.disconnect();
        wsClientRef.current = null;
      }
      isInitializedRef.current = false;
    };
  }, [onMessageCallback, requestConnectionInfo]);

  const sendMessage = useCallback((message) => {
    if (wsClientRef.current) {
      wsClientRef.current.send(message);
    }
  }, []);

  return {
    websocket,
    connectionId,
    isWebSocketConnected,
    error,
    sendMessage
  };
};

export default useWebSocket;