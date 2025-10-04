import { useEffect, useRef } from 'react';
import './App.css';
import { useWebSocket } from './hooks/useWebSocket';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';

// Automatically detect WebSocket URL based on current location
const getWebSocketUrl = () => {
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }

  // If running through Caddy (port 8080), use same host
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.hostname;
  const port = window.location.port === '8080' ? '8080' : '3000';

  return `${protocol}//${host}:${port}/ws/chat`;
};

const WS_URL = getWebSocketUrl();

function App() {
  const { isConnected, messages, streamingMessage, sendMessage } = useWebSocket(WS_URL);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, streamingMessage]);

  return (
    <div className="app">
      <div className={`connection-status ${isConnected ? 'connected' : ''}`}>
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>
      <div className="chat-container" ref={chatContainerRef}>
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} message={msg} />
        ))}
        {streamingMessage && <ChatMessage message={streamingMessage} />}
      </div>
      <ChatInput onSend={sendMessage} disabled={!isConnected} />
    </div>
  );
}

export default App;
