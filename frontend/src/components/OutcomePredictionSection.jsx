import SectionCard from './SectionCard.jsx';
import StatusBadge from './StatusBadge.jsx';
import ProbabilityDistributionBar from './ProbabilityDistributionBar.jsx';
import ApplicabilityNotice from './ApplicabilityNotice.jsx';

export function OutcomePredictionSection({
  prediction = null,
  isSummaryConfirmed = false,
  isLoading = false,
  errorMessage = '',
}) {
  const hasPrediction = Boolean(prediction);
  const normalizedClass = (prediction?.predictedClass || '').trim().toLowerCase();
  const isPositive =
    normalizedClass === 'accepted' ||
    normalizedClass === 'allowed' ||
    prediction?.predictedOutcome === 'Appeal Accepted' ||
    prediction?.predictedOutcome === 'Appeal Allowed';

  const outcomeBadge = isLoading ? (
    <StatusBadge variant="neutral">Computing...</StatusBadge>
  ) : errorMessage ? (
    <StatusBadge variant="red">Prediction Unavailable</StatusBadge>
  ) : hasPrediction ? (
    <StatusBadge variant={isPositive ? 'green' : 'red'}>
      {prediction.predictedOutcome}
    </StatusBadge>
  ) : (
    <StatusBadge variant="neutral">
      {isSummaryConfirmed ? 'Awaiting Model Inference' : 'Pending Confirmation'}
    </StatusBadge>
  );

  const confidenceDisplay =
    hasPrediction && typeof prediction.confidence === 'number'
      ? `${prediction.confidence.toFixed(1)}%`
      : '--.-%';

  const applicableProvisions = Array.isArray(prediction?.applicableProvisions)
    ? prediction.applicableProvisions.filter(Boolean)
    : [];
  const legalBasisNote = (prediction?.legalBasisNote || '').trim();
  const hasLegalBasis =
    hasPrediction && (applicableProvisions.length > 0 || Boolean(legalBasisNote));

  return (
    <SectionCard
      id="section-prediction"
      eyebrow="04 / EXPERIMENTAL RESEARCH"
      title="Appeal outcome prediction"
      subtitle="Outcome probability estimation using the Experiment 3 Random Forest model trained on structured Supreme Court of India appellate case features."
      badge={<StatusBadge variant="sage">Random Forest (Experiment 3)</StatusBadge>}
    >
      <div className="prediction-inner-card">
        <div className="prediction-row">
          <span className="prediction-label">PREDICTED OUTCOME</span>
          {outcomeBadge}
        </div>

        <div className="prediction-row">
          <span className="prediction-confidence-label">Model Confidence</span>
          <span className="prediction-confidence-value">{confidenceDisplay}</span>
        </div>

        <ProbabilityDistributionBar
          acceptedProbability={prediction?.acceptedProbability}
          rejectedProbability={prediction?.rejectedProbability}
          positiveLabel="Accepted"
          negativeLabel="Rejected"
        />

        {hasLegalBasis && (
          <div className="prediction-provisions" aria-label="Contributing legal provisions">
            <span className="prediction-label">CONTRIBUTING ARTICLES &amp; SECTIONS</span>
            {applicableProvisions.length > 0 && (
              <div className="prediction-provisions__list">
                {applicableProvisions.map((item) => (
                  <span key={item} className="prediction-provisions__item">
                    {item}
                  </span>
                ))}
              </div>
            )}
            {legalBasisNote && (
              <p className="prediction-provisions__note">{legalBasisNote}</p>
            )}
          </div>
        )}

        {errorMessage && (
          <p className="intake-error" role="alert" style={{ marginTop: '14px' }}>
            {errorMessage}
          </p>
        )}

        <div className="prediction-meta-footer">
          <span>
            <strong>Architecture:</strong> Random Forest Classifier (Experiment 3)
          </span>
          <span>
            <strong>Classes:</strong> 2 (Accepted / Rejected)
          </span>
          {hasPrediction && prediction.featureCount && (
            <span>
              <strong>Features:</strong> {prediction.featureCount.toLocaleString()}
            </span>
          )}
          {hasPrediction && typeof prediction.matchedTfidfTerms === 'number' && (
            <span>
              <strong>Matched Vocab:</strong> {prediction.matchedTfidfTerms} terms (
              {prediction.inputMode === 'firac_structured' ? 'FIRAC' : 'Direct'})
            </span>
          )}
        </div>
      </div>

      <ApplicabilityNotice matchedTfidfTerms={prediction?.matchedTfidfTerms ?? null} />
    </SectionCard>
  );
}

export default OutcomePredictionSection;
