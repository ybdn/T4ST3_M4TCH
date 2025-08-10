import React from 'react';

export interface AppHeaderProps {
  title?: string;
  onBack?: () => void;
  rightActions?: React.ReactNode;
}

const AppHeader: React.FC<AppHeaderProps> = ({ title, onBack, rightActions }) => {
  return (
      <header className="fixed top-0 left-0 right-0 z-50 font-inter safe-area-top">
        <div 
          className="h-10 md:h-16 relative px-3 md:px-6 md:tm-glass-card md:backdrop-blur-xl md:border-b md:border-white/10 header-mobile-transparent"
          style={{ 
            paddingTop: 'env(safe-area-inset-top)'
          }}
        >
          {/* Section gauche - Retour */}
          <div className="absolute left-3 md:left-6 top-0 h-10 md:h-16 flex items-center">
            {onBack && (
              <button
                onClick={onBack}
                className="p-0.5 md:p-2 text-tm-text-muted hover:text-white transition-colors duration-200 focus:outline-none"
                aria-label="Retour"
              >
                <svg className="w-4 h-4 md:w-5 md:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
              </button>
            )}
          </div>

          {/* Centre - Titre (centré absolu) */}
          <div className="absolute inset-0 flex items-center justify-center">
            <h1 className="font-cinzel text-white tracking-wide text-lg md:text-xl" style={{ margin: 0, padding: 0 }}>
              {title || "T4ST3 M4TCH"}
            </h1>
          </div>

          {/* Section droite - Actions */}
          <div className="absolute right-3 md:right-6 top-0 h-10 md:h-16 flex items-center">
            {rightActions}
          </div>
        </div>
      </header>
  );
};

export default AppHeader;