export function MessageComposer({
  value,
  onChange,
  onSubmit,
  isSending,
  hasConversationStarted,
}) {
  const placeholder = hasConversationStarted
    ? 'Answer the question or add another important fact...'
    : 'For example: My employer has not paid my salary for three months...';

  const canSend = value.trim().length > 0 && !isSending;

  const handleSubmit = (event) => {
    event.preventDefault();
    if (canSend) {
      onSubmit();
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      if (canSend) {
        onSubmit();
      }
    }
  };

  return (
    <form className="composer-form" onSubmit={handleSubmit}>
      <textarea
        className="composer-textarea"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        aria-label="Describe your legal issue or answer the follow-up question"
        disabled={isSending}
      />

      <div className="composer-actions">
        <button type="submit" className="btn btn--primary" disabled={!canSend}>
          <span>{isSending ? 'Sending...' : 'Send message'}</span>
          <span aria-hidden="true">↗</span>
        </button>
      </div>
    </form>
  );
}

export default MessageComposer;
