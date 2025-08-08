import React, { useState, useEffect } from 'react';
import { useErrorHandler } from '../hooks/useErrorHandler';
import cacheService from '../services/cacheService';
import clsx from 'clsx';

// --- Icônes SVG ---
const AddIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg> );
const RefreshIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h5M20 20v-5h-5M4 4l1.5 1.5A9 9 0 0120.5 15M20 20l-1.5-1.5A9 9 0 003.5 9" /></svg> );
const TrendingUpIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg> );
const LightbulbIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg> );

// --- Interfaces ---
interface Suggestion { /* ... */ }
interface SuggestionCardsProps { /* ... */ }

const SuggestionCards: React.FC<SuggestionCardsProps> = ({ /* ...props... */ }) => {
  // ... (logique de fetch et de handlers reste la même)

  if (loading) {
    return (
      <div>
        {title && <div className="h-8 bg-gray-700 rounded w-1/2 mb-4 animate-pulse"></div>}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {Array.from({ length: limit }).map((_, index) => (
            <div key={index} className="bg-tm-surface-light rounded-lg h-48 animate-pulse"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 text-red-400 p-4 rounded-lg flex justify-between items-center">
        <span>{error.message}</span>
        <button onClick={fetchSuggestions} className="p-1 rounded-full hover:bg-white/10"><RefreshIcon className="h-5 w-5" /></button>
      </div>
    );
  }

  if (suggestions.length === 0) {
    return (
      <div className="text-center py-8 text-tm-text-secondary">
        <p>Aucune suggestion pour le moment.</p>
        <button onClick={fetchSuggestions} className="mt-4 flex items-center gap-2 mx-auto px-4 py-2 border border-tm-border rounded-lg hover:bg-tm-surface">
          <RefreshIcon className="h-5 w-5" />
          Recharger
        </button>
      </div>
    );
  }

  return (
    <div>
      {title && (
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-tm-text-primary">{title}</h2>
          {showRefresh && <button onClick={fetchSuggestions} disabled={loading} className="p-1 rounded-full hover:bg-white/10"><RefreshIcon className="h-5 w-5" /></button>}
        </div>
      )}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {suggestions.map((suggestion, index) => (
          <div key={index} className="bg-tm-surface-light rounded-lg shadow-lg flex flex-col p-4 transition-transform duration-200 hover:-translate-y-1">
            <div className="flex-grow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-bold text-lg text-tm-text-primary line-clamp-2">{suggestion.title}</h3>
                {!category && <span className={clsx('px-2 py-0.5 text-xs font-semibold text-white rounded-full', getCategoryColor(suggestion.category))}>{suggestion.category_display}</span>}
              </div>
              <p className="text-sm text-tm-text-secondary line-clamp-3 mb-2">{suggestion.description}</p>
            </div>
            <div className="flex justify-between items-center mt-auto">
              <span className="text-xs text-tm-text-secondary flex items-center gap-1">
                {getSuggestionTypeIcon(suggestion.type, suggestion.popularity)} {getSuggestionTypeLabel(suggestion.type, suggestion.popularity)}
              </span>
              <button onClick={() => handleAdd(suggestion, index)} disabled={addingIds.has(index)} className={clsx('px-4 py-2 text-sm font-semibold text-white rounded-lg flex items-center gap-2', getCategoryColor(suggestion.category))}>
                <AddIcon className="h-5 w-5" />
                {addingIds.has(index) ? 'Ajout...' : 'Ajouter'}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SuggestionCards;
