import SectionCard from './SectionCard.jsx';
import StatusBadge from './StatusBadge.jsx';
import CaseSummaryForm, { CaseSummaryPlaceholder } from './CaseSummaryForm.jsx';

export function CaseSummarySection({
  summary,
  isConfirmed,
  errors,
  onChangeField,
  onSaveRevision,
  onConfirmSummary,
  isSaving,
  isConfirming,
  feedbackMessage,
}) {
  const hasSummary = Boolean(summary);

  const badge = hasSummary ? (
    isConfirmed ? (
      <StatusBadge variant="green">Confirmed ✓</StatusBadge>
    ) : (
      <StatusBadge variant="amber">Review required</StatusBadge>
    )
  ) : null;

  const subtitle = hasSummary
    ? 'This is a preliminary placeholder summary. Review the fields and correct anything before confirming.'
    : undefined;

  return (
    <SectionCard
      id="section-summary"
      eyebrow="02 / REVIEW THE FACTS"
      title="Case summary"
      subtitle={subtitle}
      badge={badge}
    >
      <div className="summary-body">
        {hasSummary ? (
          <CaseSummaryForm
            values={summary}
            errors={errors}
            onChangeField={onChangeField}
            onSaveRevision={onSaveRevision}
            onConfirmSummary={onConfirmSummary}
            isSaving={isSaving}
            isConfirming={isConfirming}
            feedbackMessage={feedbackMessage}
          />
        ) : (
          <CaseSummaryPlaceholder />
        )}
      </div>
    </SectionCard>
  );
}

export default CaseSummarySection;
