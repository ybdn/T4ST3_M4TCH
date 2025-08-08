import React, { useState } from 'react';
import AppHeader from '../components/AppHeader';
import AppBottomNav from '../components/AppBottomNav';
import clsx from 'clsx';

// --- Icônes SVG ---
const ThumbUpIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" strokeWidth={0}><path d="M2 20h2c.55 0 1-.45 1-1v-9c0-.55-.45-1-1-1H2v11zm19.83-7.12c.11-.25.17-.52.17-.8V8c0-1.1-.9-2-2-2h-4.26l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 0 7.58 6.59C7.22 6.95 7 7.45 7 8v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05z" /></svg> );
const ThumbDownIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" strokeWidth={0}><path d="M22 4h-2c-.55 0-1 .45-1 1v9c0 .55.45 1 1 1h2V4zM2.17 11.12c-.11.25-.17.52-.17.8V16c0 1.1.9 2 2 2h4.26l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 24l6.59-6.59C16.78 17.05 17 16.55 17 16V6c0-1.1-.9-2-2-2H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05z" /></svg> );
const RefreshIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h5M20 20v-5h-5M4 4l1.5 1.5A9 9 0 0120.5 15M20 20l-1.5-1.5A9 9 0 003.5 9" /></svg> );

// --- Interfaces ---
interface MatchItem {
  id: string;
  title: string;
  description: string;
  category: string;
  compatibilityScore: number;
  reasons: string[];
}

interface MatchPageProps {
  onNavigate?: (section: string) => void;
}

const MatchPage: React.FC<MatchPageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(2); // Match est à l'index 2
  const [currentMatch, setCurrentMatch] = useState(0);
  
  // Données d'exemple pour les matchs
  const matches: MatchItem[] = [
    {
      id: '1',
      title: 'Blade Runner 2049',
      description: 'Un chef-d\'œuvre visuel de science-fiction qui explore l\'humanité.',
      category: 'Films',
      compatibilityScore: 92,
      reasons: ['Sci-Fi', 'Visuel époustouflant', 'Philosophique']
    },
    {
      id: '2',
      title: 'Stranger Things',
      description: 'Une série nostalgique qui mélange horreur et aventure.',
      category: 'Séries',
      compatibilityScore: 87,
      reasons: ['Nostalgique', 'Mystère', 'Personnages attachants']
    },
    {
      id: '3',
      title: 'Bohemian Rhapsody',
      description: 'L\'histoire captivante du groupe Queen et de Freddie Mercury.',
      category: 'Musique',
      compatibilityScore: 95,
      reasons: ['Rock classique', 'Biopic', 'Performance épique']
    }
  ];

  const currentItem = matches[currentMatch] || matches[0];

  const handleBottomNavChange = (_event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'profil'];
    onNavigate?.(sections[newValue]);
  };

  const handleLike = () => {
    if (currentMatch < matches.length - 1) {
      setCurrentMatch(currentMatch + 1);
    } else {
      // Fin des matchs
      console.log('Tous les matchs terminés !');
    }
  };

  const handleDislike = () => {
    if (currentMatch < matches.length - 1) {
      setCurrentMatch(currentMatch + 1);
    } else {
      // Fin des matchs
      console.log('Tous les matchs terminés !');
    }
  };

  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="T4ST3 M4TCH" />

      <div className="h-[calc(100vh-9rem)] flex flex-col px-4 sm:px-6 lg:px-8">
        
        {/* Card de match - centrée et sans scroll */}
        <div className="flex-1 flex items-center justify-center">
          <div className="w-full max-w-sm tm-glass-card rounded-xl p-6 text-center">
            
            {/* Score de compatibilité */}
            <div className="mb-4">
              <p className="text-5xl font-bold text-tm-primary mb-1">{currentItem.compatibilityScore}%</p>
              <p className="text-xs text-tm-text-muted">Compatibilité</p>
            </div>
            
            {/* Badge catégorie */}
            <span className="inline-block px-3 py-1 text-xs font-semibold bg-tm-primary/20 text-tm-primary rounded-full mb-4">
              {currentItem.category}
            </span>
            
            {/* Titre */}
            <h1 className="text-xl font-bold font-cinzel text-white mb-3">{currentItem.title}</h1>
            
            {/* Description */}
            <p className="text-sm text-tm-text-muted mb-4 leading-relaxed line-clamp-3">{currentItem.description}</p>
            
            {/* Raisons du match */}
            <div className="mb-6">
              <h2 className="text-sm font-semibold text-tm-text mb-2">Pourquoi ce match ?</h2>
              <div className="flex flex-wrap justify-center gap-1">
                {currentItem.reasons.map(reason => (
                  <span key={reason} className="px-2 py-1 text-xs tm-glass rounded-full text-tm-text-muted">
                    {reason}
                  </span>
                ))}
              </div>
            </div>

            {/* Boutons d'action */}
            <div className="flex gap-6 justify-center">
              <button 
                onClick={handleDislike} 
                className="w-16 h-16 flex items-center justify-center bg-red-500/20 text-red-400 rounded-full hover:bg-red-500/30 hover:scale-110 transition-all duration-200"
              >
                <ThumbDownIcon className="h-7 w-7" />
              </button>
              <button 
                onClick={handleLike} 
                className="w-16 h-16 flex items-center justify-center bg-green-500/20 text-green-400 rounded-full hover:bg-green-500/30 hover:scale-110 transition-all duration-200"
              >
                <ThumbUpIcon className="h-7 w-7" />
              </button>
            </div>
          </div>
        </div>

        {/* Espace pour la navbar */}
        <div className="pb-2"></div>
      </div>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />
    </div>
  );
};

export default MatchPage;
