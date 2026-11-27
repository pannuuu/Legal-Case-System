export function ProbabilityDistributionBar({
  acceptedProbability,
  rejectedProbability,
  positiveLabel = 'Accepted',
  negativeLabel = 'Rejected',
}) {
  const hasValues =
    typeof acceptedProbability === 'number' && typeof rejectedProbability === 'number';

  const positiveWidth = hasValues ? Math.max(0, Math.min(100, acceptedProbability)) : 0;
  const negativeWidth = hasValues ? Math.max(0, Math.min(100, rejectedProbability)) : 0;

  return (
    <div className="prob-section">
      <span className="prediction-label">PROBABILITY DISTRIBUTION</span>

      <div
        className="prob-bar-track"
        role="img"
        aria-label={
          hasValues
            ? `Probability distribution: ${positiveLabel} ${positiveWidth.toFixed(1)}%, ${negativeLabel} ${negativeWidth.toFixed(1)}%`
            : 'Probability distribution awaiting model inference'
        }
      >
        {hasValues && (
          <>
            <div
              className="prob-bar-segment--allowed"
              style={{ width: `${positiveWidth}%` }}
            />
            <div
              className="prob-bar-segment--dismissed"
              style={{ width: `${negativeWidth}%` }}
            />
          </>
        )}
      </div>

      <div className="prob-bar-legend">
        <span className={hasValues ? 'prob-legend__allowed' : 'prob-legend__pending'}>
          {positiveLabel}: {hasValues ? `${positiveWidth.toFixed(1)}%` : '--.-%'}
        </span>
        <span className={hasValues ? 'prob-legend__dismissed' : 'prob-legend__pending'}>
          {negativeLabel}: {hasValues ? `${negativeWidth.toFixed(1)}%` : '--.-%'}
        </span>
      </div>
    </div>
  );
}

export default ProbabilityDistributionBar;
