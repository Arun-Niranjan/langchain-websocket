export function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`msg ${isUser ? 'user' : 'ai'}`}>
      {!isUser && (
        <>
          {message.title && <div className="title">{message.title}</div>}
          {message.haiku && <div className="haiku">{message.haiku}</div>}
          {message.content && <div>{message.content}</div>}
        </>
      )}
      {isUser && <div>{message.content}</div>}
    </div>
  );
}
