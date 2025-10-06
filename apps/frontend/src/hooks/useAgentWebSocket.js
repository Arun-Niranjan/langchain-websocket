import { useEffect, useRef, useState } from 'react';

export function useAgentWebSocket(url) {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [streamingContent, setStreamingContent] = useState('');
  const [toolCalls, setToolCalls] = useState([]);
  const wsRef = useRef(null);
  const streamingContentRef = useRef('');
  const toolCallsRef = useRef([]);

  // Keep refs in sync with state
  useEffect(() => {
    streamingContentRef.current = streamingContent;
  }, [streamingContent]);

  useEffect(() => {
    toolCallsRef.current = toolCalls;
  }, [toolCalls]);

  useEffect(() => {
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      console.log('Received message:', msg);

      switch (msg.type) {
        case 'start':
          // Reset streaming state for new response
          setStreamingContent('');
          setToolCalls([]);
          break;

        case 'tool_call':
          // Add tool call to list
          setToolCalls((prev) => [
            ...prev,
            {
              id: msg.tool_call_id,
              name: msg.tool_name,
              args: msg.tool_args,
              result: null,
            },
          ]);
          break;

        case 'tool_result':
          // Update tool call with result
          setToolCalls((prev) =>
            prev.map((tc) =>
              tc.id === msg.tool_call_id ? { ...tc, result: msg.result } : tc
            )
          );
          break;

        case 'content_delta':
          // Update streaming content with accumulated text
          setStreamingContent(msg.accumulated);
          break;

        case 'content_complete':
          // Finalize content
          setStreamingContent(msg.content);
          break;

        case 'end':
          // Add completed message with all tool calls and content using refs
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: streamingContentRef.current,
              toolCalls: toolCallsRef.current,
              timestamp: msg.timestamp,
            },
          ]);
          setStreamingContent('');
          setToolCalls([]);
          break;

        case 'error':
          // Add error message
          setMessages((prev) => [
            ...prev,
            {
              role: 'error',
              content: msg.message,
              code: msg.code,
            },
          ]);
          setStreamingContent('');
          setToolCalls([]);
          break;

        default:
          console.warn('Unknown message type:', msg.type);
      }
    };

    return () => {
      if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
        ws.close();
      }
    };
  }, [url]);

  const sendMessage = (text) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(text);
      setMessages((prev) => [
        ...prev,
        {
          role: 'user',
          content: text,
        },
      ]);
    }
  };

  return {
    isConnected,
    messages,
    streamingContent,
    toolCalls,
    sendMessage,
  };
}
