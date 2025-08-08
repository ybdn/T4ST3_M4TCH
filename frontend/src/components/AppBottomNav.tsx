import React from 'react';

export interface AppBottomNavProps {
  value: number;
  onChange: (event: React.SyntheticEvent, newValue: number) => void;
}

const AppBottomNav: React.FC<AppBottomNavProps> = ({ value, onChange }) => {
  const navItems = [
    { 
      label: 'Accueil', 
      icon: 'home',
      activeColor: '#e11d48'
    },
    { 
      label: 'Découvrir', 
      icon: 'explore',
      activeColor: '#3b82f6'
    },
    { 
      label: 'MATCH !', 
      icon: 'heart',
      activeColor: '#ef4444'
    },
    { 
      label: 'Listes', 
      icon: 'list',
      activeColor: '#10b981'
    },
    { 
      label: 'Profil', 
      icon: 'profile',
      activeColor: '#8b5cf6'
    },
  ];

  const handleClick = (index: number) => {
    onChange(null as any, index);
  };

  const renderIcon = (iconName: string, isActive: boolean, activeColor: string) => {
    const className = `w-5 h-5 transition-all duration-200`;
    
    switch (iconName) {
      case 'home':
        return (
          <svg className={className} fill={isActive ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24" strokeWidth={isActive ? 0 : 2}>
            <path strokeLinecap="round" strokeLinejoin="round" d={isActive ? "M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" : "M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"} />
          </svg>
        );
      case 'explore':
        return (
          <svg className={className} fill={isActive ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24" strokeWidth={isActive ? 0 : 2}>
            <path strokeLinecap="round" strokeLinejoin="round" d={isActive ? "M12 10.9c-.61 0-1.1.49-1.1 1.1s.49 1.1 1.1 1.1c.61 0 1.1-.49 1.1-1.1s-.49-1.1-1.1-1.1zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm2.19 12.19L6 18l3.81-8.19L18 6l-3.81 8.19z" : "M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"} />
          </svg>
        );
      case 'heart':
        return (
          <svg className={className} fill={isActive ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24" strokeWidth={isActive ? 0 : 2}>
            <path strokeLinecap="round" strokeLinejoin="round" d={isActive ? "M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" : "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"} />
          </svg>
        );
      case 'list':
        return (
          <svg className={className} fill={isActive ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24" strokeWidth={isActive ? 0 : 2}>
            <path strokeLinecap="round" strokeLinejoin="round" d={isActive ? "M3 13h2v-2H3v2zm0 4h2v-2H3v2zm0-8h2V7H3v2zm4 4h14v-2H7v2zm0 4h14v-2H7v2zM7 7v2h14V7H7z" : "M4 6h16M4 10h16M4 14h16M4 18h16"} />
          </svg>
        );
      case 'profile':
        return (
          <svg className={className} fill={isActive ? "currentColor" : "none"} stroke="currentColor" viewBox="0 0 24 24" strokeWidth={isActive ? 0 : 2}>
            <path strokeLinecap="round" strokeLinejoin="round" d={isActive ? "M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z" : "M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"} />
          </svg>
        );
      default:
        return null;
    }
  };

  return (
      <nav className="fixed bottom-0 left-0 right-0 z-50 font-inter">
        <div 
          className="tm-glass-card backdrop-blur-xl border-t border-white/10"
          style={{ 
            height: '5rem',
            background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%)',
            boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 -1px 20px rgba(0, 0, 0, 0.3)'
          }}
        >
          <div className="flex items-center justify-around h-full px-4">
            {navItems.map((item, index) => (
              <button
                key={index}
                onClick={() => handleClick(index)}
                className="relative flex flex-col items-center p-2 transition-all duration-200 focus:outline-none"
                style={{
                  minWidth: '4rem'
                }}
              >
                {/* Indicateur actif */}
                {value === index && (
                  <div 
                    className="absolute -top-2 w-8 h-1 rounded-full bg-white"
                    style={{
                      boxShadow: '0 0 8px rgba(255, 255, 255, 0.6)'
                    }}
                  />
                )}
                
                <div 
                  className="mb-1"
                  style={{
                    color: value === index ? '#ffffff' : '#71767b'
                  }}
                >
                  {renderIcon(item.icon, value === index, item.activeColor)}
                </div>
                
                <span 
                  className="text-xs font-medium transition-colors duration-200"
                  style={{
                    color: value === index ? '#ffffff' : '#71767b'
                  }}
                >
                  {item.label}
                </span>
              </button>
            ))}
          </div>
        </div>
      </nav>
  );
};

export default AppBottomNav;