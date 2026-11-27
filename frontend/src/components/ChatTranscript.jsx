import { useEffect, useRef } from 'react';
import ChatMessageBubble from './ChatMessageBubble.jsx';
import EmptyStateBox from './EmptyStateBox.jsx';

export function ChatTranscript({ messages, isSending }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isSending]);

  if (messages.length === 0 && !isSending) {
    return (
      <div className="chat-transcript chat-transcript--empty">
        <EmptyStateBox
          icon={
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 2L14.5 9.5L22 12L14.5 14.5L12 22L9.5 14.5L2 12L9.5 9.5L12 2Z" />
            </svg>
          }
          title="What happened?"
          description="Describe the legal issue you would like to understand."
        />
      </div>
    );
  }

  return (
    <div ref={scrollRef} className="chat-transcript" aria-live="polite">
      {messages.map((msg) => (
        <ChatMessageBubble key={msg.id} role={msg.role} content={msg.content} />
      ))}

      {isSending && (
        <div className="chat-row chat-row--assistant" aria-label="Assistant is typing">
          <span className="chat-avatar chat-avatar--ai" aria-hidden="true">
            AI
          </span>
          <div className="typing-pill">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatTranscript;
