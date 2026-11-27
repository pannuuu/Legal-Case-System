export function ApplicabilityNotice({ matchedTfidfTerms = null }) {
  const showLowCoverageHint =
    typeof matchedTfidfTerms === 'number' && matchedTfidfTerms > 0 && matchedTfidfTerms < 50;

  return (
    <div className="applicability-notice" role="note" aria-label="Academic and legal applicability notice">
      <p className="applicability-notice__title">ACADEMIC &amp; LEGAL APPLICABILITY NOTICE</p>
      <ul className="applicability-notice__list">
        <li>
          The Experiment 3 Random Forest classifier was trained on completed Supreme Court appellate
          judgment texts and reflects historical appellate distributions.
        </li>
        <li>
          User case summaries are converted into a neutral FIRAC representation before inference,
          which remains a statistical approximation and does not reflect unrepresented evidentiary
          nuances.
        </li>
        {showLowCoverageHint && (
          <li>
            Low appellate vocabulary overlap ({matchedTfidfTerms} of 50,000 TF-IDF terms matched):
            short pre-litigation descriptions carry sparse judgment-style signals and should be
            interpreted cautiously alongside the retrieved precedents.
          </li>
        )}
        <li>
          Outcome probabilities must be interpreted as academic predictions and not legal advice or
          guarantees of judicial outcome.
        </li>
      </ul>
    </div>
  );
}

export default ApplicabilityNotice;
