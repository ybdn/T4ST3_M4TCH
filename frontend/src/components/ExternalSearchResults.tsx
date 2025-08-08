import React, { useState, useEffect } from 'react';
import { useFeedback } from '../context/FeedbackContext';
import cacheService from '../services/cacheService';
import clsx from 'clsx';

// --- Icônes SVG ---
const AddIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg> );
const InfoIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg> );
const StarIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="currentColor" viewBox="0 0 24 24" strokeWidth={0}><path strokeLinecap="round" strokeLinejoin="round" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.196-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.783-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" /></svg> );

// --- Interfaces ---
interface ExternalSearchResult { /* ... */ }
interface ExternalSearchResultsProps { /* ... */ }

const ExternalSearchResults: React.FC<ExternalSearchResultsProps> = ({ /* ...props... */ }) => {
  // ... (logique de fetch et de handlers reste la même)

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="bg-tm-surface-light rounded-lg h-96 animate-pulse"></div>
        ))}
      </div>
    );
  }

  if (error) {
    return <div className="bg-red-500/10 text-red-400 p-4 rounded-lg">{error}</div>;
  }

  if (results.length === 0) {
    return (
      <div className="text-center py-8 text-tm-text-secondary">
        <p>Aucun résultat trouvé pour "{query}"</p>
        <p className="text-sm">Essayez avec d'autres mots-clés.</p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">Résultats externes <span className="text-sm font-normal text-tm-text-secondary">({results.length})</span></h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {results.map((result) => (
          <div key={result.external_id} className="bg-tm-surface-light rounded-lg shadow-lg flex flex-col cursor-pointer transition-transform duration-200 hover:-translate-y-1" onClick={() => handleSelect(result)}>
            <img src={result.poster_url || '/vite.svg'} alt={result.title} className="h-64 w-full object-cover rounded-t-lg" />
            <div className="p-4 flex flex-col flex-grow">
              <h3 className="font-bold text-lg text-tm-text-primary mb-1 line-clamp-2">{result.title}</h3>
              <div className="flex items-center gap-2 text-xs text-tm-text-secondary mb-2">
                {result.rating && <span className="flex items-center gap-1"><StarIcon className="h-4 w-4 text-yellow-400" /> {result.rating.toFixed(1)}</span>}
                {result.release_date && <span>{formatDate(result.release_date)}</span>}
              </div>
              <p className="text-sm text-tm-text-secondary line-clamp-3 flex-grow">{result.description || 'Aucune description'}</p>
              <div className="flex justify-between items-center mt-4">
                <span className={clsx('px-2 py-1 text-xs font-semibold text-white rounded-full', getCategoryConfig(result.category).color)}>{result.category_display}</span>
                {onAdd && (
                  <button disabled={addingIds.has(result.external_id)} onClick={(e) => { e.stopPropagation(); handleAdd(result); }} className="p-2 rounded-full bg-primary text-white hover:bg-primary/80 disabled:bg-gray-500">
                    <AddIcon className="h-5 w-5" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExternalSearchResults;