const NAV_ITEMS = [
  { id: 'guidance', label: 'Guidance' },
  { id: 'judgments', label: 'Similar Judgments' },
  { id: 'prediction', label: 'Outcome Prediction' },
];

export function Header({ activeTab, onSelectTab, onNewCase, isConnected = true }) {
  return (
    <header className="app-header">
      <div className="app-header__inner">
        <div className="brand-block">
          <div className="brand-block__logo" aria-hidden="true">
            §
          </div>
          <div className="brand-block__text">
            <span className="brand-block__title">AI Legal Guidance</span>
            <span className="brand-block__subtitle">Indian legal context</span>
          </div>
        </div>

        <div className="header-controls">
          <nav className="header-nav" aria-label="Primary navigation">
            {NAV_ITEMS.map((item) => {
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  className={`header-nav__tab ${isActive ? 'header-nav__tab--active' : ''}`}
                  aria-current={isActive ? 'page' : undefined}
                  onClick={() => onSelectTab(item.id)}
                >
                  {item.label}
                </button>
              );
            })}
          </nav>

          <div className="header-actions">
            <button type="button" className="new-case-btn" onClick={onNewCase}>
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
                <path d="M3 3v5h5" />
              </svg>
              <span>New case</span>
            </button>

            <span className="connection-status" aria-live="polite">
              <span
                className={`connection-status__dot ${
                  isConnected ? '' : 'connection-status__dot--offline'
                }`}
              />
              <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
