import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import AppHeader from '../components/AppHeader';
import AppBottomNav from '../components/AppBottomNav';

interface HomePageProps {
  onNavigate?: (section: string) => void;
}

const HomePage: React.FC<HomePageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(0);
  const { user } = useAuth();

  const handleBottomNavChange = (_event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'profil'];
    onNavigate?.(sections[newValue]);
  };

  const quickActions = [
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
        </svg>
      ),
      title: 'Ajout rapide',
      description: 'Ajoutez rapidement vos découvertes',
      action: () => onNavigate?.('ajout')
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      title: 'Créer une liste',
      description: 'Organisez vos découvertes par thème',
      action: () => onNavigate?.('listes')
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      ),
      title: 'Découvrir',
      description: 'Explorez de nouveaux contenus tendance',
      action: () => onNavigate?.('decouvrir')
    },
    {
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      ),
      title: 'Faire un match',
      description: 'Comparez vos goûts avec vos amis',
      action: () => onNavigate?.('match')
    }
  ];

  const stats = [
    { label: 'Listes', value: '3', color: 'text-tm-primary' },
    { label: 'Matchs', value: '12', color: 'text-white' },
    { label: 'Tendances', value: '+18%', color: 'text-green-400' },
    { label: 'Favoris', value: '25', color: 'text-blue-400' },
  ];

  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="T4ST3 M4TCH" />

        <div className="h-[calc(100vh-4rem)] overflow-y-auto pb-20">
          <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
            
            {/* Hero Section avec proportions dorées */}
            <section className="text-left">
              <h1 className="text-lg xs:text-xl sm:text-2xl md:text-3xl lg:phi-title font-cinzel text-white mb-4 break-words leading-tight">
                Bienvenue, {user?.username} ! ✨
              </h1>
              <p className="text-sm sm:phi-description text-tm-text-muted leading-relaxed">
                Découvrez, partagez et jouez avec vos amis dans l'univers de T4ST3 M4TCH
              </p>
            </section>

            {/* Statistiques avec effets de verre */}
            <section className="tm-glass-card rounded-xl p-6">
              <h2 className="phi-subtitle font-cinzel text-tm-text text-center mb-6">
                Vos statistiques
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {stats.map((stat, index) => (
                  <div key={stat.label} className="tm-glass p-6 rounded-xl text-center" style={{
                    boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(255, 255, 255, 0.05)'
                  }}>
                    <div className={`text-2xl font-bold ${stat.color} mb-2`}>
                      {stat.value}
                    </div>
                    <div className="text-sm text-tm-text-muted">
                      {stat.label}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Actions rapides avec verre premium */}
            <section className="tm-glass-card rounded-xl p-6">
              <h2 className="phi-subtitle font-cinzel text-tm-text mb-6">
                Actions rapides
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {quickActions.map((action, index) => (
                  <button
                    key={action.title}
                    onClick={action.action}
                    className="w-full tm-glass p-6 rounded-xl text-left group hover:scale-[1.02] transition-all duration-200"
                    style={{
                      boxShadow: 'inset 0 1px 0 rgba(255, 255, 255, 0.15), 0 4px 12px rgba(255, 255, 255, 0.05)'
                    }}
                  >
                    <div className="flex items-start gap-4">
                      <div className="p-3 tm-glass-card rounded-xl text-tm-primary group-hover:text-white transition-colors duration-200 flex-shrink-0">
                        {action.icon}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-semibold text-white group-hover:text-tm-primary transition-colors duration-200 mb-1">
                          {action.title}
                        </h3>
                        <p className="text-sm text-tm-text-muted line-clamp-2">
                          {action.description}
                        </p>
                      </div>
                      <div className="text-tm-text-muted group-hover:text-white transition-colors duration-200 flex-shrink-0">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </section>

            {/* CTA Principal avec bouton verre premium */}
            <section className="text-center">
              <button
                onClick={() => onNavigate?.('ajout')}
                className="tm-glass-button phi-button inline-flex items-center justify-center gap-2 rounded-xl focus:outline-none focus:ring-2 focus:ring-white/50 text-lg font-bold px-8 py-4 mb-4"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Ajout rapide
              </button>
              <p className="phi-description text-tm-text-muted max-w-md mx-auto">
                Commencez par ajouter votre premier élément
              </p>
            </section>

          </div>
        </div>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />
    </div>
  );
};

export default HomePage;