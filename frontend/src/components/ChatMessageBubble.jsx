export function ChatMessageBubble({ role, content }) {
  const isUser = role === 'user';

  return (
    <div className={`chat-row ${isUser ? 'chat-row--user' : 'chat-row--assistant'}`}>
      {!isUser && (
        <span className="chat-avatar chat-avatar--ai" aria-hidden="true">
          AI
        </span>
      )}

      <div className={`chat-bubble ${isUser ? 'chat-bubble--user' : 'chat-bubble--assistant'}`}>
        <span className="chat-bubble__role">{isUser ? 'YOU' : 'ASSISTANT'}</span>
        <p className="chat-bubble__text">{content}</p>
      </div>

      {isUser && (
        <span className="chat-avatar chat-avatar--user" aria-hidden="true">
          You
        </span>
      )}
    </div>
  );
}

export default ChatMessageBubble;
