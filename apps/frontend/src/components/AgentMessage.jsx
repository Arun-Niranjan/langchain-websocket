export function AgentMessage({ message, streamingContent, toolCalls }) {
  const isUser = message?.role === 'user';
  const isError = message?.role === 'error';

  if (isUser) {
    return (
      <div className="msg user">
        <div>{message.content}</div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="msg error">
        <div style={{ color: '#ff4444' }}>
          Error: {message.content} {message.code && `(${message.code})`}
        </div>
      </div>
    );
  }

  // Assistant message or streaming
  return (
    <div className="msg ai">
      {/* Show tool calls */}
      {(toolCalls || message?.toolCalls)?.length > 0 && (
        <div className="tool-calls">
          {(toolCalls || message.toolCalls).map((tc) => (
            <div key={tc.id} className="tool-call">
              <div className="tool-name">🔧 {tc.name}</div>
              {tc.args && Object.keys(tc.args).length > 0 && (
                <div className="tool-args">
                  <code>{JSON.stringify(tc.args, null, 2)}</code>
                </div>
              )}
              {tc.result !== null && (
                <div className="tool-result">
                  <strong>Result:</strong>
                  <pre>{JSON.stringify(tc.result, null, 2)}</pre>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Show content */}
      {(streamingContent || message?.content) && (
        <div className="content">
          {streamingContent || message.content}
        </div>
      )}
    </div>
  );
}
