import EmptyStateBox from './EmptyStateBox.jsx';

export function CaseSummaryForm({
  values,
  errors,
  onChangeField,
  onSaveRevision,
  onConfirmSummary,
  isSaving,
  isConfirming,
  feedbackMessage,
}) {
  const isBusy = isSaving || isConfirming;

  return (
    <form
      className="summary-form"
      onSubmit={(event) => {
        event.preventDefault();
        onConfirmSummary();
      }}
      noValidate
    >
      <div className="summary-grid-row">
        <div className="summary-field">
          <label className="summary-field__label" htmlFor="summary-problem-type">
            PROBLEM TYPE
          </label>
          <input
            id="summary-problem-type"
            type="text"
            className={`summary-input ${errors.problemType ? 'summary-input--error' : ''}`}
            value={values.problemType}
            onChange={(event) => onChangeField('problemType', event.target.value)}
            disabled={isBusy}
          />
          {errors.problemType && (
            <span className="summary-field__error">{errors.problemType}</span>
          )}
        </div>

        <div className="summary-field">
          <label className="summary-field__label" htmlFor="summary-jurisdiction">
            JURISDICTION
          </label>
          <input
            id="summary-jurisdiction"
            type="text"
            className={`summary-input ${errors.jurisdiction ? 'summary-input--error' : ''}`}
            value={values.jurisdiction}
            onChange={(event) => onChangeField('jurisdiction', event.target.value)}
            disabled={isBusy}
          />
          {errors.jurisdiction && (
            <span className="summary-field__error">{errors.jurisdiction}</span>
          )}
        </div>
      </div>

      <div className="summary-field">
        <label className="summary-field__label" htmlFor="summary-key-facts">
          KEY FACTS
        </label>
        <textarea
          id="summary-key-facts"
          className={`summary-textarea ${errors.keyFacts ? 'summary-textarea--error' : ''}`}
          value={values.keyFacts}
          onChange={(event) => onChangeField('keyFacts', event.target.value)}
          disabled={isBusy}
        />
        {errors.keyFacts && <span className="summary-field__error">{errors.keyFacts}</span>}
      </div>

      <div className="summary-grid-row">
        <div className="summary-field">
          <label className="summary-field__label" htmlFor="summary-claimed-harm">
            CLAIMED HARM
          </label>
          <input
            id="summary-claimed-harm"
            type="text"
            className={`summary-input ${errors.claimedHarm ? 'summary-input--error' : ''}`}
            value={values.claimedHarm}
            onChange={(event) => onChangeField('claimedHarm', event.target.value)}
            disabled={isBusy}
          />
          {errors.claimedHarm && (
            <span className="summary-field__error">{errors.claimedHarm}</span>
          )}
        </div>

        <div className="summary-field">
          <label className="summary-field__label" htmlFor="summary-requested-outcome">
            REQUESTED OUTCOME
          </label>
          <input
            id="summary-requested-outcome"
            type="text"
            className={`summary-input ${errors.requestedOutcome ? 'summary-input--error' : ''}`}
            value={values.requestedOutcome}
            onChange={(event) => onChangeField('requestedOutcome', event.target.value)}
            disabled={isBusy}
          />
          {errors.requestedOutcome && (
            <span className="summary-field__error">{errors.requestedOutcome}</span>
          )}
        </div>
      </div>

      <div className="summary-footer">
        {feedbackMessage && (
          <span className="summary-feedback" role="status">
            {feedbackMessage}
          </span>
        )}

        <div className="summary-buttons">
          <button
            type="button"
            className="btn btn--secondary"
            onClick={onSaveRevision}
            disabled={isBusy}
          >
            {isSaving ? 'Saving...' : 'Save revision'}
          </button>

          <button type="submit" className="btn btn--primary" disabled={isBusy}>
            <span>{isConfirming ? 'Confirming...' : 'Confirm summary'}</span>
            <span aria-hidden="true">✓</span>
          </button>
        </div>
      </div>
    </form>
  );
}

export function CaseSummaryPlaceholder() {
  return (
    <EmptyStateBox
      icon={
        <svg
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          aria-hidden="true"
        >
          <rect x="4" y="4" width="16" height="16" rx="2" />
        </svg>
      }
      title="Your summary will appear here"
      description="Send a message to begin collecting the key details."
    />
  );
}

export default CaseSummaryForm;
