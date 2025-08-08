import React from 'react';

export interface AppHeaderProps {
  title?: string;
  onBack?: () => void;
  rightActions?: React.ReactNode;
}

const AppHeader: React.FC<AppHeaderProps> = ({ title, onBack, rightActions }) => {
  return (
      <header className="sticky top-0 z-50 font-inter">
        <div 
          className="tm-glass-card backdrop-blur-xl border-b border-white/10 h-16 relative px-6"
          style={{ 
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%)',
            boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 1px 20px rgba(0, 0, 0, 0.3)'
          }}
        >
          {/* Section gauche - Retour */}
          <div className="absolute left-6 top-0 h-16 flex items-center">
            {onBack && (
              <button
                onClick={onBack}
                className="p-2 text-tm-text-muted hover:text-white transition-colors duration-200 focus:outline-none"
                aria-label="Retour"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            )}
          </div>

          {/* Centre - Titre (centré absolu) */}
          <div className="absolute inset-0 flex items-center justify-center">
            <h1 className="font-cinzel text-white tracking-wide" style={{ fontSize: '1.618rem', lineHeight: '1.618', margin: 0, padding: 0 }}>
              {title || "T4ST3 M4TCH"}
            </h1>
          </div>

          {/* Section droite - Actions */}
          <div className="absolute right-6 top-0 h-16 flex items-center">
            {rightActions}
          </div>
        </div>
      </header>
  );
};

export default AppHeader;