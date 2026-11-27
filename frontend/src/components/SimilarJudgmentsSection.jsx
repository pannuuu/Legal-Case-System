import SectionCard from './SectionCard.jsx';
import StatusBadge from './StatusBadge.jsx';
import EmptyStateBox from './EmptyStateBox.jsx';
import JudgmentCard from './JudgmentCard.jsx';

export function SimilarJudgmentsSection({
  judgments = [],
  isSummaryConfirmed = false,
  isLoading = false,
  isPreview = false,
  errorMessage = '',
}) {
  const hasResults = judgments.length > 0;

  const badge = hasResults ? (
    <StatusBadge variant="sage">Generation: Verified</StatusBadge>
  ) : (
    <StatusBadge variant="neutral">Persistent Vector Index</StatusBadge>
  );

  return (
    <SectionCard
      id="section-judgments"
      eyebrow="03 / EXPLORE REFERENCES"
      title="Similar judgments"
      subtitle="Authentic Supreme Court of India precedents retrieved by semantic similarity to your confirmed case summary."
      badge={badge}
    >
      {!isPreview && (
        <>
          <div className="judgments-meta-bar">
            <p className="judgments-count">
              {isLoading
                ? 'Searching persistent precedent index...'
                : errorMessage
                  ? 'Precedent retrieval unavailable'
                  : hasResults
                    ? `Retrieved ${judgments.length} relevant precedent passages`
                    : isSummaryConfirmed
                      ? 'Ready for precedent retrieval'
                      : 'Awaiting confirmed case summary'}
            </p>
            {hasResults && <StatusBadge variant="sage">Generation: Verified</StatusBadge>}
          </div>

          {isLoading ? (
            <EmptyStateBox
              title="Retrieving precedent passages..."
              description="Querying the persistent vector index for relevant Supreme Court excerpts."
            />
          ) : errorMessage ? (
            <EmptyStateBox
              title="Unable to reach retrieval backend"
              description={errorMessage}
            />
          ) : hasResults ? (
            <>
              <div className="judgments-list">
                {judgments.map((item, idx) => (
                  <JudgmentCard key={item.id || `${item.title}-${idx}`} judgment={item} />
                ))}
              </div>
              <p className="judgments-footnote">
                Note: Retrieved from persistent index of authentic Supreme Court judgments.
                Passages are verified verbatim excerpts.
              </p>
            </>
          ) : (
            <EmptyStateBox
              icon={
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="1.8"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  aria-hidden="true"
                >
                  <path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" />
                </svg>
              }
              title={
                isSummaryConfirmed
                  ? 'No matching precedent passages found'
                  : 'Confirm your case summary first'
              }
              description={
                isSummaryConfirmed
                  ? 'No passages met the retrieval criteria for the current summary.'
                  : 'Complete Section 01 and confirm your case summary in Section 02 to unlock semantic precedent search.'
              }
            />
          )}
        </>
      )}
    </SectionCard>
  );
}

export default SimilarJudgmentsSection;
