import React, { useState, useEffect } from 'react';
import AppHeader from '../components/AppHeader';
import AppBottomNav from '../components/AppBottomNav';
import { useVersusSession } from '../hooks/useVersusSession';

// --- Icônes SVG ---
const ThumbUpIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" strokeWidth={0}><path d="M2 20h2c.55 0 1-.45 1-1v-9c0-.55-.45-1-1-1H2v11zm19.83-7.12c.11-.25.17-.52.17-.8V8c0-1.1-.9-2-2-2h-4.26l.95-4.57.03-.32c0-.41-.17-.79-.44-1.06L14.17 0 7.58 6.59C7.22 6.95 7 7.45 7 8v10c0 1.1.9 2 2 2h9c.83 0 1.54-.5 1.84-1.22l3.02-7.05z" /></svg> );
const ThumbDownIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" strokeWidth={0}><path d="M22 4h-2c-.55 0-1 .45-1 1v9c0 .55.45 1 1 1h2V4zM2.17 11.12c-.11.25-.17.52-.17.8V16c0 1.1.9 2 2 2h4.26l-.95 4.57-.03.32c0 .41.17.79.44 1.06L9.83 24l6.59-6.59C16.78 17.05 17 16.55 17 16V6c0-1.1-.9-2-2-2H6c-.83 0-1.54.5-1.84 1.22l-3.02 7.05z" /></svg> );
const RefreshIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h5M20 20v-5h-5M4 4l1.5 1.5A9 9 0 0120.5 15M20 20l-1.5-1.5A9 9 0 003.5 9" /></svg> );

interface MatchPageProps {
  onNavigate?: (section: string) => void;
}

const MatchPage: React.FC<MatchPageProps> = ({ onNavigate }) => {
  const [bottomNavValue, setBottomNavValue] = useState(2); // Match est à l'index 2
  const [isAnimating, setIsAnimating] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  
  const { 
    session, 
    currentRound, 
    summary,
    loading, 
    submittingChoice,
    submitChoice,
    createSession,
    refetchRound,
    isSessionFinished,
    canSubmitChoice,
    progressPercentage,
    currentScore
  } = useVersusSession();

  // Gestion de l'affichage du résumé
  useEffect(() => {
    if (isSessionFinished && summary) {
      setShowSummary(true);
    }
  }, [isSessionFinished, summary]);

  const handleBottomNavChange = (_event: React.SyntheticEvent, newValue: number) => {
    setBottomNavValue(newValue);
    const sections = ['accueil', 'decouvrir', 'match', 'listes', 'profil'];
    onNavigate?.(sections[newValue]);
  };

  const handleChoice = async (choice: 'like' | 'dislike' | 'skip') => {
    if (!canSubmitChoice) return;

    // Animation de choix
    setIsAnimating(true);
    
    // Délai pour l'animation
    setTimeout(async () => {
      const result = await submitChoice(choice);
      setIsAnimating(false);
      
      if (!result) {
        // En cas d'erreur, essayer de resynchroniser
        await refetchRound();
      }
    }, 300);
  };

  const handleNewSession = async () => {
    setShowSummary(false);
    await createSession(10);
  };

  const handleReturnHome = () => {
    setShowSummary(false);
    onNavigate?.('accueil');
  };

  // État de chargement
  if (loading && !session) {
    return (
      <div className="min-h-screen tm-auth-bg font-inter flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-tm-primary mx-auto mb-4"></div>
          <p className="text-tm-text">Chargement de votre session...</p>
        </div>
      </div>
    );
  }

  // Écran de résumé de fin de session
  if (showSummary && summary) {
    return (
      <div className="min-h-screen tm-auth-bg font-inter">
        <AppHeader title="T4ST3 M4TCH" />
        
        <div className="h-[calc(100vh-9rem)] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
          <div className="w-full max-w-sm tm-glass-card rounded-xl p-6 text-center">
            <h1 className="text-2xl font-bold font-cinzel text-white mb-4">
              Session Terminée ! 🎉
            </h1>
            
            <div className="space-y-4 mb-6">
              <div className="text-3xl font-bold text-tm-primary">
                {summary.total_score} pts
              </div>
              
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div className="text-center">
                  <div className="text-green-400 text-xl">👍</div>
                  <div className="text-tm-text">{summary.likes}</div>
                </div>
                <div className="text-center">
                  <div className="text-red-400 text-xl">👎</div>
                  <div className="text-tm-text">{summary.dislikes}</div>
                </div>
                <div className="text-center">
                  <div className="text-blue-400 text-xl">⏭️</div>
                  <div className="text-tm-text">{summary.skips}</div>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <button 
                onClick={handleNewSession}
                className="w-full py-3 bg-tm-primary text-white rounded-lg hover:bg-tm-primary/80 transition-colors"
              >
                Nouvelle Session
              </button>
              <button 
                onClick={handleReturnHome}
                className="w-full py-3 tm-glass text-tm-text rounded-lg hover:bg-white/10 transition-colors"
              >
                Retour à l'accueil
              </button>
            </div>
          </div>
        </div>

        <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />
      </div>
    );
  }

  // Pas de round disponible
  if (!currentRound && !loading) {
    return (
      <div className="min-h-screen tm-auth-bg font-inter">
        <AppHeader title="T4ST3 M4TCH" />
        
        <div className="h-[calc(100vh-9rem)] flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
          <div className="w-full max-w-sm tm-glass-card rounded-xl p-6 text-center">
            <h2 className="text-xl font-semibold text-tm-text mb-4">
              Aucun contenu disponible
            </h2>
            <p className="text-tm-text-muted mb-6">
              Impossible de charger le contenu pour cette session.
            </p>
            <button 
              onClick={handleNewSession}
              className="w-full py-3 bg-tm-primary text-white rounded-lg hover:bg-tm-primary/80 transition-colors"
            >
              Créer une nouvelle session
            </button>
          </div>
        </div>

        <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />
      </div>
    );
  }

  return (
    <div className="min-h-screen tm-auth-bg font-inter">
      <AppHeader title="T4ST3 M4TCH" />

      <div className="h-[calc(100vh-9rem)] flex flex-col px-4 sm:px-6 lg:px-8">
        
        {/* Barre de progression */}
        {session && (
          <div className="w-full bg-black/20 rounded-full h-2 mb-4 mt-4">
            <div 
              className="bg-tm-primary h-2 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        )}

        {/* Informations de session */}
        {session && (
          <div className="flex justify-between items-center mb-4 text-sm text-tm-text-muted">
            <span>Round {session.current_round}/{session.total_rounds}</span>
            <span>Score: {currentScore} pts</span>
          </div>
        )}
        
        {/* Card de match - centrée et sans scroll */}
        <div className="flex-1 flex items-center justify-center py-4">
          <div 
            className={`w-full max-w-sm tm-glass-card rounded-xl overflow-hidden transition-all duration-300 ${
              isAnimating ? 'scale-95 opacity-70' : 'scale-100 opacity-100'
            }`} 
            style={{ height: '75vh', maxHeight: '600px' }}
          >            
            {currentRound && (
              <>
                {/* Image de couverture */}
                <div className="relative h-1/2 overflow-hidden">
                  <img
                    src={currentRound.item_poster_url || '/vite.svg'}
                    alt={currentRound.item_title}
                    className="w-full h-full object-cover"
                    onError={(e: React.SyntheticEvent<HTMLImageElement>) => { 
                      e.currentTarget.src = '/vite.svg'; 
                    }}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                  
                  {/* Score de compatibilité en overlay */}
                  <div className="absolute top-4 right-4 bg-white/10 backdrop-blur-md rounded-full px-3 py-2">
                    <p className="text-2xl font-bold text-white">{currentRound.compatibility_score}%</p>
                    <p className="text-xs text-white/80 text-center">Match</p>
                  </div>
                  
                  {/* Badge catégorie en overlay */}
                  <div className="absolute top-4 left-4">
                    <span className="px-3 py-1 text-xs font-semibold bg-tm-primary text-white rounded-full">
                      {currentRound.item_category}
                    </span>
                  </div>
                </div>
                
                {/* Contenu */}
                <div className="h-1/2 p-6 flex flex-col justify-between text-center">
                  {/* Contenu principal */}
                  <div className="flex-1">
                    {/* Titre */}
                    <h1 className="text-xl font-bold font-cinzel text-white mb-2">{currentRound.item_title}</h1>
                    
                    {/* Description */}
                    <p className="text-sm text-tm-text-muted mb-3 leading-relaxed line-clamp-3">{currentRound.item_description}</p>
                  </div>

                  {/* Boutons d'action */}
                  <div className="flex gap-4 justify-center">
                    <button 
                      onClick={() => handleChoice('dislike')}
                      disabled={!canSubmitChoice || submittingChoice}
                      className="w-14 h-14 flex items-center justify-center bg-red-500/20 text-red-400 rounded-full hover:bg-red-500/30 hover:scale-110 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                    >
                      <ThumbDownIcon className="h-6 w-6" />
                    </button>
                    <button 
                      onClick={() => handleChoice('skip')}
                      disabled={!canSubmitChoice || submittingChoice}
                      className="w-14 h-14 flex items-center justify-center bg-blue-500/20 text-blue-400 rounded-full hover:bg-blue-500/30 hover:scale-110 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                    >
                      <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                      </svg>
                    </button>
                    <button 
                      onClick={() => handleChoice('like')}
                      disabled={!canSubmitChoice || submittingChoice}
                      className="w-14 h-14 flex items-center justify-center bg-green-500/20 text-green-400 rounded-full hover:bg-green-500/30 hover:scale-110 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                    >
                      <ThumbUpIcon className="h-6 w-6" />
                    </button>
                  </div>
                  
                  {/* Indicateur de chargement */}
                  {submittingChoice && (
                    <div className="mt-4 flex items-center justify-center">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-tm-primary"></div>
                    </div>
                  )}
                </div>
              </>
            )}
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
