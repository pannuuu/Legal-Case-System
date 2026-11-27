export function HeroBanner() {
  return (
    <section className="hero-banner" aria-labelledby="hero-heading">
      <div className="hero-banner__content">
        <p className="hero-banner__eyebrow">ACADEMIC LEGAL TECHNOLOGY PROTOTYPE</p>
        <h1 id="hero-heading" className="hero-banner__title">
          <span className="hero-banner__title-primary">Understand your case.</span>
          <span className="hero-banner__title-accent">Explore what comes next.</span>
        </h1>
        <p className="hero-banner__subtitle">
          A structured starting point for understanding legal concerns in the Indian context — with
          transparent limitations, persistent precedent retrieval, and experimental outcome
          modeling.
        </p>
      </div>

      <aside className="hero-disclaimer" aria-label="Educational disclaimer">
        <svg
          className="hero-disclaimer__icon"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.8"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10" />
          <line x1="12" y1="16" x2="12" y2="12" />
          <line x1="12" y1="8" x2="12.01" y2="8" />
        </svg>
        <p className="hero-disclaimer__text">
          For educational purposes only. Not a substitute for professional legal advice.
        </p>
      </aside>
    </section>
  );
}

export default HeroBanner;
