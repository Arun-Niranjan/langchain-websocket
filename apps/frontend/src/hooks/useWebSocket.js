import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url) {
  const [isConnected, setIsConnected] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState(null);
  const [messages, setMessages] = useState([]);
  const wsRef = useRef(null);

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
      const resp = JSON.parse(event.data);
      const msg = resp.message || {};

      if (resp.type === 'start') {
        setStreamingMessage({
          role: 'ai',
          title: null,
          content: null,
          haiku: null,
        });
      } else if (resp.type === 'stream') {
        setStreamingMessage((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            title: msg.title ?? prev.title,
            content: msg.content ?? prev.content,
            haiku: msg.haiku ?? prev.haiku,
          };
        });
      } else if (resp.type === 'end') {
        setStreamingMessage((prev) => {
          if (!prev) return null;
          const finalMessage = {
            ...prev,
            title: msg.title ?? prev.title,
            content: msg.content ?? prev.content,
            haiku: msg.haiku ?? prev.haiku,
          };
          setMessages((msgs) => [...msgs, finalMessage]);
          return null;
        });
      } else if (resp.type === 'error') {
        const errorMsg = {
          role: 'ai',
          title: null,
          content: msg.content || 'Error',
          haiku: null,
        };
        setMessages((msgs) => [...msgs, errorMsg]);
        setStreamingMessage(null);
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
      setMessages((msgs) => [
        ...msgs,
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
    streamingMessage,
    sendMessage,
  };
}
