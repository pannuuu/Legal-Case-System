import StatusBadge from './StatusBadge.jsx';

export function JudgmentCard({ judgment }) {
  const {
    court = 'SUPREME COURT OF INDIA',
    similarityScore,
    date,
    title,
    citation,
    excerpt,
    offsetStart,
    offsetEnd,
    context,
  } = judgment;

  const formattedScore =
    typeof similarityScore === 'number' ? `${similarityScore.toFixed(1)}% match` : null;

  const hasOffsets = offsetStart !== undefined && offsetEnd !== undefined;

  return (
    <article className="judgment-card">
      <div className="judgment-card__top">
        <span className="judgment-card__court">{court}</span>
        <div className="judgment-card__metrics">
          {formattedScore && <StatusBadge variant="lime">{formattedScore}</StatusBadge>}
          {date && <span className="judgment-card__date">{date}</span>}
        </div>
      </div>

      <h3 className="judgment-card__title">{title}</h3>
      {citation && <p className="judgment-card__citation">Case: {citation}</p>}

      <div className="excerpt-box">
        <div className="excerpt-box__header">
          <span className="excerpt-box__label">VERBATIM PASSAGE EXCERPT</span>
          {hasOffsets && (
            <span className="excerpt-box__offsets">
              Offsets: [{offsetStart} : {offsetEnd}]
            </span>
          )}
        </div>
        <p className="excerpt-box__body">{excerpt}</p>
      </div>

      {context && (
        <p className="judgment-card__context">
          <strong>Context:</strong> {context}
        </p>
      )}
    </article>
  );
}

export default JudgmentCard;
