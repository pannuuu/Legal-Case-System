export function EmptyStateBox({ icon, title, description }) {
  return (
    <div className="empty-state-box">
      {icon && <div className="empty-state-box__icon">{icon}</div>}
      <h3 className="empty-state-box__title">{title}</h3>
      {description && <p className="empty-state-box__description">{description}</p>}
    </div>
  );
}

export default EmptyStateBox;
