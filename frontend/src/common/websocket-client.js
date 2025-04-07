/**
 * WebSocket client for connecting to the Bedrock streaming API
 */
class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.connection = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.onOpen = null;
    this.onMessage = null;
    this.onClose = null;
    this.onError = null;
  }

  /**
   * Connect to the WebSocket server
   */
  connect() {
    if (this.connection && (this.connection.readyState === WebSocket.CONNECTING || 
                           this.connection.readyState === WebSocket.OPEN)) {
      console.log('WebSocket connection already exists');
      return;
    }

    console.log(`Connecting to WebSocket at ${this.url}`);
    this.connection = new WebSocket(this.url);

    this.connection.onopen = (event) => {
      console.log('WebSocket connection opened');
      this.reconnectAttempts = 0;
      if (this.onOpen) this.onOpen(event);
    };

    this.connection.onmessage = (event) => {
      if (this.onMessage) {
        try {
          const data = JSON.parse(event.data);
          this.onMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
          this.onMessage({ error: 'Failed to parse message' });
        }
      }
    };

    this.connection.onclose = (event) => {
      console.log('WebSocket connection closed', event);
      if (this.onClose) this.onClose(event);
      this._attemptReconnect();
    };

    this.connection.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (this.onError) this.onError(error);
    };
  }

  /**
   * Send a message to the WebSocket server
   * @param {Object} data - The data to send
   */
  send(data) {
    if (!this.connection || this.connection.readyState !== WebSocket.OPEN) {
      console.error('Cannot send message, WebSocket is not connected');
      return false;
    }

    try {
      this.connection.send(JSON.stringify(data));
      return true;
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      return false;
    }
  }

  /**
   * Close the WebSocket connection
   */
  disconnect() {
    if (this.connection) {
      this.connection.close();
    }
  }

  /**
   * Attempt to reconnect to the WebSocket server
   * @private
   */
  _attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);
      
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`);
      
      setTimeout(() => {
        this.connect();
      }, delay);
    } else {
      console.error('Maximum reconnect attempts reached');
    }
  }
}

export default WebSocketClient;