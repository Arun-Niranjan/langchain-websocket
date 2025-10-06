import { useEffect, useRef } from 'react';
import { useAgentWebSocket } from '../hooks/useAgentWebSocket';
import { AgentMessage } from '../components/AgentMessage';
import { ChatInput } from '../components/ChatInput';

// Automatically detect WebSocket URL based on current location
const getWebSocketUrl = () => {
  if (import.meta.env.VITE_AGENT_WS_URL) {
    return import.meta.env.VITE_AGENT_WS_URL;
  }

  // If running through Caddy (port 8080), use same host
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.hostname;
  const port = window.location.port === '8080' ? '8080' : '3000';

  return `${protocol}//${host}:${port}/ws/agent`;
};

const WS_URL = getWebSocketUrl();

export function AgentChat() {
  const { isConnected, messages, streamingContent, toolCalls, sendMessage } =
    useAgentWebSocket(WS_URL);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, streamingContent, toolCalls]);

  const isStreaming = streamingContent || toolCalls.length > 0;

  return (
    <div className="app">
      <div className={`connection-status ${isConnected ? 'connected' : ''}`}>
        {isConnected ? 'Connected' : 'Disconnected'}
      </div>
      <div className="chat-container" ref={chatContainerRef}>
        {messages.map((msg, idx) => (
          <AgentMessage key={idx} message={msg} />
        ))}
        {isStreaming && (
          <AgentMessage
            streamingContent={streamingContent}
            toolCalls={toolCalls}
          />
        )}
      </div>
      <ChatInput onSend={sendMessage} disabled={!isConnected} />
    </div>
  );
}
