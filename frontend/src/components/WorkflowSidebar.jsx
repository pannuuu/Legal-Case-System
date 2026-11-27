export function WorkflowSidebar({ steps, onSelectStep }) {
  return (
    <aside className="workflow-sidebar" aria-label="Workflow progress and guidance notice">
      <div className="workflow-card">
        <p className="workflow-card__eyebrow">YOUR WORKFLOW</p>
        <ol className="workflow-steps">
          {steps.map((step) => {
            const numClass = step.completed
              ? 'workflow-step__num workflow-step__num--completed'
              : step.active
                ? 'workflow-step__num workflow-step__num--active'
                : 'workflow-step__num';

            return (
              <li key={step.number} className="workflow-step">
                <button
                  type="button"
                  className="workflow-step__btn"
                  onClick={() => onSelectStep?.(step.target)}
                >
                  <span className={numClass}>{step.number}</span>
                  <span className="workflow-step__info">
                    <span className="workflow-step__title">{step.title}</span>
                    <span className="workflow-step__subtitle">{step.subtitle}</span>
                  </span>
                </button>
              </li>
            );
          })}
        </ol>
      </div>

      <div className="advisory-card">
        <div className="advisory-card__header">
          <svg
            className="advisory-card__icon"
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.9"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z" />
            <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z" />
            <path d="M7 21h10" />
            <path d="M12 3v18" />
            <path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2" />
          </svg>
          <h3 className="advisory-card__title">Stay informed</h3>
        </div>
        <p className="advisory-card__text">
          AI-generated guidance can be incomplete. Always consult a qualified legal professional for
          advice.
        </p>
      </div>
    </aside>
  );
}

export default WorkflowSidebar;
