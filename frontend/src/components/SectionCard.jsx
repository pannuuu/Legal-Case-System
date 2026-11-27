export function SectionCard({ id, eyebrow, title, subtitle, badge, children }) {
  return (
    <section id={id} className="section-card">
      <div className="section-card-header">
        <div>
          {eyebrow && <p className="eyebrow-label">{eyebrow}</p>}
          <h2 className="section-card-title">{title}</h2>
        </div>
        {badge && <div className="section-card-badge">{badge}</div>}
      </div>
      {subtitle && <p className="section-card-subtitle">{subtitle}</p>}
      {children}
    </section>
  );
}

export default SectionCard;
