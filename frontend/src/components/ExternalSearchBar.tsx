import React, { useState, useEffect, useCallback } from 'react';
import { Combobox, Transition } from '@headlessui/react';
import clsx from 'clsx';
import { API_BASE_URL } from '../config';

// --- Icônes SVG ---
const SearchIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg> );
const ClearIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg> );
const AddIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg> );

// --- Interfaces ---
interface ExternalSearchResult {
  external_id: string;
  source: string;
  category: string;
  category_display: string;
  title: string;
  description?: string;
  poster_url?: string;
  release_date?: string;
}

interface ExternalSearchBarProps {
  showSourceFilter?: boolean;
  onSelect?: (result: ExternalSearchResult) => void;
  onQuickAdd?: (result: ExternalSearchResult) => void;
  placeholder?: string;
  onSuggestionsToggle?: (isVisible: boolean) => void;
  onResultsCount?: (count: number) => void;
}

const ExternalSearchBar: React.FC<ExternalSearchBarProps> = ({ 
  showSourceFilter, 
  onSelect, 
  onQuickAdd,
  placeholder = "Rechercher des films, séries, musiques, livres...",
  onSuggestionsToggle,
  onResultsCount
}) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<ExternalSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedResult, setSelectedResult] = useState<ExternalSearchResult | null>(null);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const handleSearch = useCallback(async (searchQuery: string) => {
    if (!searchQuery || searchQuery.length < 2) {
      setResults([]);
      setShowSuggestions(false);
      return;
    }
    
    setIsLoading(true);
    setShowSuggestions(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${API_BASE_URL}/search/external/?q=${encodeURIComponent(searchQuery)}&limit=8`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Erreur lors de la recherche');
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('Erreur de recherche:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Debounce pour éviter trop de requêtes
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      handleSearch(query);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, handleSearch]);

  // Notifier le parent quand les suggestions changent
  useEffect(() => {
    const shouldShow = showSuggestions && (results.length > 0 || isLoading);
    onSuggestionsToggle?.(shouldShow);
  }, [showSuggestions, results.length, isLoading, onSuggestionsToggle]);

  // Notifier le parent du nombre de résultats
  useEffect(() => {
    onResultsCount?.(results.length);
  }, [results.length, onResultsCount]);

  const handleInputChange = (value: string) => {
    setQuery(value);
    if (!value || value.length < 2) {
      setShowSuggestions(false);
    }
  };

  const closeSuggestions = () => {
    setShowSuggestions(false);
    setResults([]);
  };

  const handleSelectResult = (result: ExternalSearchResult) => {
    setSelectedResult(result);
    setShowSuggestions(false);
    if (result && onSelect) {
      onSelect(result);
    }
  };

  return (
    <Combobox
      value={selectedResult}
      onChange={handleSelectResult}
    >
      <div className="relative w-full">
        <div className="flex items-center gap-3">
          <div className="relative flex-1">
            <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <Combobox.Input
              className="w-full tm-glass-input rounded-xl pl-10 pr-10 py-3 text-tm-text placeholder:text-tm-text-muted focus:outline-none focus:ring-2 focus:ring-tm-primary"
              displayValue={() => query}
              onChange={(event) => handleInputChange(event.target.value)}
              onFocus={() => {
                if (query.length >= 2 && results.length > 0) {
                  setShowSuggestions(true);
                }
              }}
              placeholder={placeholder}
            />
            {isLoading && (
              <div className="absolute right-10 top-1/2 -translate-y-1/2 w-5 h-5 border-2 border-t-transparent border-tm-primary rounded-full animate-spin"></div>
            )}
            {query && !isLoading && (
              <button 
                onClick={() => {
                  setQuery('');
                  closeSuggestions();
                }} 
                className="absolute right-3 top-1/2 -translate-y-1/2 p-1 hover:bg-white/10 rounded"
              >
                <ClearIcon className="h-4 w-4 text-tm-text-muted" />
              </button>
            )}
          </div>
          
        </div>

        <Transition
          show={showSuggestions && (results.length > 0 || isLoading || query.length >= 2)}
          enter="transition duration-100 ease-out"
          enterFrom="transform scale-95 opacity-0"
          enterTo="transform scale-100 opacity-100"
          leave="transition duration-75 ease-out"
          leaveFrom="transform scale-100 opacity-100"
          leaveTo="transform scale-95 opacity-0"
        >
          <Combobox.Options className="absolute z-10 mt-1 w-full tm-glass-card rounded-xl shadow-xl max-h-80 overflow-auto">
            {results.length === 0 && query !== '' && !isLoading ? (
              <div className="p-4 text-center text-tm-text-muted">
                Aucun résultat trouvé
              </div>
            ) : (
              results.map((result) => (
                <Combobox.Option
                  key={result.external_id}
                  className={({ active }) =>
                    clsx(
                      'relative p-4 flex items-center gap-4 cursor-pointer transition-colors duration-200',
                      active ? 'bg-tm-primary/20' : 'hover:bg-white/5'
                    )
                  }
                  value={result}
                >
                  <img 
                    src={result.poster_url || ''} 
                    alt={result.title} 
                    className="w-12 h-16 object-cover rounded-md bg-tm-surface" 
                    onError={(e) => {
                      (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNjQiIHZpZXdCb3g9IjAgMCA0OCA2NCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjQ4IiBoZWlnaHQ9IjY0IiBmaWxsPSIjMzc0MTUxIi8+Cjx0ZXh0IHg9IjI0IiB5PSIzMiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0iIzZCNzI4MCIgZm9udC1zaXplPSIxMiI+Tj9BPC90ZXh0Pgo8L3N2Zz4K';
                    }}
                  />
                  <div className="flex-grow min-w-0">
                    <h4 className="font-semibold text-tm-text truncate">{result.title}</h4>
                    <p className="text-sm text-slate-300 line-clamp-2 leading-relaxed">{result.description}</p>
                    <div className="flex items-center gap-2 mt-2 text-xs">
                      <span className="px-3 py-1 bg-tm-primary text-white rounded-full font-semibold">
                        {result.category_display}
                      </span>
                      <span className="px-2 py-1 bg-slate-700 text-slate-200 rounded-full font-medium">
                        {result.source.toUpperCase()}
                      </span>
                      {result.release_date && (
                        <span className="text-slate-300 font-medium">
                          {new Date(result.release_date).getFullYear()}
                        </span>
                      )}
                    </div>
                  </div>
                  {onQuickAdd && (
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        onQuickAdd(result);
                        closeSuggestions();
                      }}
                      className="ml-4 p-2 text-red-400 hover:text-red-300 border border-red-400 hover:border-red-300 rounded-full transition-colors duration-200"
                    >
                      <AddIcon className="h-5 w-5" />
                    </button>
                  )}
                </Combobox.Option>
              ))
            )}
          </Combobox.Options>
        </Transition>
      </div>
    </Combobox>
  );
};

export default ExternalSearchBar;
