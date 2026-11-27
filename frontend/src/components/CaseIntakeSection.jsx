import SectionCard from './SectionCard.jsx';
import StatusBadge from './StatusBadge.jsx';
import ChatTranscript from './ChatTranscript.jsx';
import NextQuestionCallout from './NextQuestionCallout.jsx';
import MessageComposer from './MessageComposer.jsx';

export function CaseIntakeSection({
  messages,
  nextQuestion,
  draftMessage,
  onDraftChange,
  onSendMessage,
  isSending,
  errorMessage = '',
}) {
  return (
    <SectionCard
      id="section-intake"
      eyebrow="01 / UNDERSTAND YOUR SITUATION"
      title="Start with your legal concern"
      subtitle="Share the facts in your own words. The assistant will ask one follow-up question at a time to build a reviewable case summary."
      badge={<StatusBadge variant="lime">Guidance</StatusBadge>}
    >
      <div className="intake-body">
        <ChatTranscript messages={messages} isSending={isSending} />
        <NextQuestionCallout question={nextQuestion} />
        {errorMessage && (
          <p className="intake-error" role="alert">
            {errorMessage}
          </p>
        )}
        <MessageComposer
          value={draftMessage}
          onChange={onDraftChange}
          onSubmit={onSendMessage}
          isSending={isSending}
          hasConversationStarted={messages.length > 0}
        />
      </div>
    </SectionCard>
  );
}

export default CaseIntakeSection;
