/**
 * Version simplifiée pour debug du composant VersusMatch
 */

import React from "react";

type VersusMatchProps = Record<string, never>; // pas de props pour la version simplifiée

const VersusMatch: React.FC<VersusMatchProps> = () => {
  return (
    <div className="space-y-6">
      <div className="tm-glass-card rounded-xl p-6 text-center">
        <div className="text-6xl mb-4">⚔️</div>
        <h2 className="text-xl font-bold text-white mb-2">
          Versus Match (Debug)
        </h2>
        <p className="text-tm-text-muted">Fonctionnalité en refonte.</p>
      </div>
    </div>
  );
};

export default VersusMatch;
