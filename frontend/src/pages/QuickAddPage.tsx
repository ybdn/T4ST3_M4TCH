import React from "react";

// Page placeholder pendant la refactorisation de l'ajout rapide.
// Objectif: éliminer les erreurs de compilation liées à l'ancien code complexe.
// Étapes futures: réintroduire recherche externe unifiée + suggestions normalisées.

const QuickAddPage: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center text-white">
      <h1 className="text-2xl font-bold mb-4">
        Fonction "Ajout rapide" en refonte
      </h1>
      <p className="text-tm-text-secondary max-w-lg mb-6">
        Nous simplifions et unifions le flux d'enrichissement des contenus
        (films, séries, livres, musique) afin d'utiliser une structure
        normalisée unique. Cette page reviendra très bientôt.
      </p>
      <div className="opacity-60 text-sm">
        Ticket interne: Refactor QuickAdd → unification external_ref
      </div>
    </div>
  );
};

export default QuickAddPage;
