export function NextQuestionCallout({ question }) {
  if (!question) {
    return null;
  }

  return (
    <div className="next-question-callout" role="region" aria-label="Next follow-up question">
      <p className="next-question-callout__label">NEXT QUESTION</p>
      <p className="next-question-callout__text">{question}</p>
    </div>
  );
}

export default NextQuestionCallout;
