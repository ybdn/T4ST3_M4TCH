import React from 'react';

const MatchPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center">
      <div className="text-center">
        <div className="text-4xl mb-4">🔧</div>
        <h1 className="text-2xl font-bold mb-2">Match Page Debug</h1>
        <p className="text-gray-400">Ultra simple - aucun import externe</p>
        <div className="mt-4 text-xs text-gray-500">
          Si cette page fonctionne, le problème vient d'AppHeader ou AppBottomNav
        </div>
      </div>
    </div>
  );
};

export default MatchPage;