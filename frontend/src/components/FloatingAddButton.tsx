import React, { useState } from "react";
import { Dialog, DialogTitle } from "@headlessui/react";
import ExternalSearchBar from "./ExternalSearchBar";
import { API_BASE_URL } from "../config";

interface ExternalSearchResult {
  external_id: string;
  source: string;
  category: string;
  title: string;
  description?: string;
  poster_url?: string;
}

interface FloatingAddButtonProps {
  onAdd?: (result: ExternalSearchResult) => void;
}

const FloatingAddButton: React.FC<FloatingAddButtonProps> = ({ onAdd }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [searchSuggestionsVisible, setSearchSuggestionsVisible] =
    useState(false);
  const [searchResultsCount, setSearchResultsCount] = useState(0);

  const handleAddItem = async (result: ExternalSearchResult) => {
    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch(`${API_BASE_URL}/import/external/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          external_id: result.external_id,
          source: result.source,
          category: result.category,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || "Erreur lors de l'ajout");
      }

      // Fermer le modal après ajout réussi
      setIsModalOpen(false);

      // Callback optionnel
      onAdd?.(result);
    } catch (error) {
      console.error("Erreur lors de l'ajout:", error);
      // TODO: Afficher une notification d'erreur
    }
  };

  return (
    <>
      {/* Bouton flottant */}
      <button
        onClick={() => setIsModalOpen(true)}
        className="fixed bottom-28 right-8 z-40 w-16 h-16 rounded-full tm-glass-card border border-white/20 flex items-center justify-center hover:scale-105 transition-all duration-300 shadow-xl backdrop-blur-sm"
        style={{
          boxShadow:
            "inset 0 1px 0 rgba(255, 255, 255, 0.2), 0 8px 32px rgba(0, 0, 0, 0.3), 0 4px 12px rgba(255, 255, 255, 0.1)",
        }}
      >
        <svg
          className="w-7 h-7 text-white drop-shadow-sm"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2.5}
            d="M12 4v16m8-8H4"
          />
        </svg>
      </button>

      {/* Modal d'ajout rapide */}
      <Dialog
        open={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        className="relative z-50"
      >
        {/* Overlay d'assombrissement */}
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-all duration-300 ease-in-out"
          aria-hidden="true"
        />

        <div className="fixed inset-0 overflow-y-auto">
          <div className="min-h-full flex flex-col">
            {/* Header du modal */}
            <div
              className={`bg-black/20 backdrop-blur-sm border-b border-white/10 transition-all duration-300 ${
                searchSuggestionsVisible ? "opacity-50" : "opacity-100"
              }`}
            >
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <DialogTitle className="text-xl font-semibold text-white font-cinzel">
                      Ajout rapide ⚡
                    </DialogTitle>
                    {searchResultsCount > 0 && (
                      <span className="flex items-center justify-center w-8 h-8 text-sm font-semibold text-tm-text-muted bg-white/10 rounded-full">
                        {searchResultsCount}
                      </span>
                    )}
                  </div>
                  <button
                    onClick={() => setIsModalOpen(false)}
                    className="text-tm-text-muted hover:text-white transition-colors"
                  >
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            {/* Contenu du modal */}
            <div className="flex-1 relative">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                {/* Description */}
                <div
                  className={`mb-6 transition-all duration-300 ${
                    searchSuggestionsVisible
                      ? "opacity-50 pointer-events-none"
                      : "opacity-100"
                  }`}
                >
                  <p className="text-tm-text-muted text-sm leading-relaxed text-center">
                    Recherchez et ajoutez rapidement des films, séries, albums
                    ou livres à vos listes.
                  </p>
                </div>

                {/* Barre de recherche */}
                <div
                  className={`transition-all duration-300 ${
                    searchSuggestionsVisible
                      ? "fixed top-20 left-0 right-0 z-20 px-4 sm:px-6 lg:px-8"
                      : ""
                  }`}
                >
                  <div
                    className={
                      searchSuggestionsVisible ? "max-w-7xl mx-auto" : ""
                    }
                  >
                    <ExternalSearchBar
                      onSelect={handleAddItem}
                      onQuickAdd={handleAddItem}
                      placeholder="Rechercher un film, série, album, livre..."
                      onSuggestionsToggle={setSearchSuggestionsVisible}
                      onResultsCount={setSearchResultsCount}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Dialog>
    </>
  );
};

export default FloatingAddButton;
