import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import AppHeader from '../components/AppHeader';
import AppBottomNav from '../components/AppBottomNav';
import FloatingAddButton from '../components/FloatingAddButton';

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


  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="T4ST3 M4TCH" />

        <div className="h-[calc(100vh-4rem)] overflow-y-auto pb-20">
          <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
            
            {/* Hero Section minimaliste */}
            <section className="text-left">
              <h1 className="text-2xl sm:text-3xl font-cinzel text-white mb-2 break-words leading-tight">
                Salut, {user?.username} ! ✨
              </h1>
            </section>

            {/* Navigation rapide - 3 cartes principales */}
            <section className="grid grid-cols-3 gap-4">
              <button
                onClick={() => onNavigate?.('decouvrir')}
                className="tm-glass-card rounded-2xl p-6 text-center group hover:scale-[1.02] transition-all duration-200"
              >
                <div className="w-12 h-12 mx-auto mb-3 p-3 tm-glass rounded-xl text-tm-primary">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <h3 className="text-white font-semibold">Explorer</h3>
                <p className="text-xs text-tm-text-muted mt-1">Tendances</p>
              </button>

              <button
                onClick={() => onNavigate?.('match')}
                className="tm-glass-card rounded-2xl p-6 text-center group hover:scale-[1.02] transition-all duration-200"
              >
                <div className="w-12 h-12 mx-auto mb-3 p-3 tm-glass rounded-xl text-tm-primary">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                </div>
                <h3 className="text-white font-semibold">Match</h3>
                <p className="text-xs text-tm-text-muted mt-1">Comparer</p>
              </button>

              <button
                onClick={() => onNavigate?.('listes')}
                className="tm-glass-card rounded-2xl p-6 text-center group hover:scale-[1.02] transition-all duration-200"
              >
                <div className="w-12 h-12 mx-auto mb-3 p-3 tm-glass rounded-xl text-tm-primary">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="text-white font-semibold">Listes</h3>
                <p className="text-xs text-tm-text-muted mt-1">Organiser</p>
              </button>
            </section>

            {/* Message de communication */}
            <section className="tm-glass-card rounded-xl p-6 border border-tm-primary/30">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 bg-gradient-to-br from-tm-primary to-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m-2 8l4-4H7a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v14l-4-4z" />
                  </svg>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-white font-semibold">Message de l'équipe</h3>
                    <span className="px-2 py-1 text-xs bg-tm-primary text-white rounded-full">Nouveau</span>
                  </div>
                  <p className="text-tm-text-muted text-sm leading-relaxed mb-3">
                    👋 Bienvenue sur T4ST3 M4TCH ! L'application est actuellement en cours de développement. 
                    De nouvelles fonctionnalités sont ajoutées régulièrement pour améliorer votre expérience de découverte culturelle.
                  </p>
                  <div className="flex items-center gap-2 text-xs text-tm-text-muted">
                    <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                    <span>Dernière mise à jour : aujourd'hui</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Activité récente */}
            <section className="tm-glass-card rounded-xl p-6">
              <h2 className="text-lg font-cinzel text-tm-text mb-4">
                Activité récente
              </h2>
              <div className="space-y-3">
                <div className="flex items-center gap-3 p-3 tm-glass rounded-lg">
                  <div className="w-8 h-8 bg-tm-primary rounded-lg flex items-center justify-center text-white text-sm font-bold">
                    🎬
                  </div>
                  <div className="flex-1">
                    <p className="text-white text-sm">Dernier ajout: Film tendance</p>
                    <p className="text-tm-text-muted text-xs">Il y a 2h</p>
                  </div>
                </div>
              </div>
            </section>


          </div>
        </div>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />
      <FloatingAddButton />
    </div>
  );
};

export default HomePage;