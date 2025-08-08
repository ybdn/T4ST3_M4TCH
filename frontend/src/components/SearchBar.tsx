import React, { useState } from 'react';
import { useCombobox } from 'downshift';
import { useDebouncedCallback } from 'use-debounce';
import clsx from 'clsx';

// --- Icônes SVG ---
const SearchIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg> );
const ClearIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg> );
const AddIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg> );

// --- Interfaces ---
interface SearchResult { /* ... */ }
interface SearchBarProps { /* ... */ }

const SearchBar: React.FC<SearchBarProps> = ({ /* ...props... */ }) => {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const debouncedSearch = useDebouncedCallback(async (query) => {
    if (!query || query.length < 2) {
      setResults([]);
      return;
    }
    setIsLoading(true);
    // ... (logique de fetch interne) ...
    setIsLoading(false);
  }, 300);

  const { isOpen, getMenuProps, getInputProps, getComboboxProps, getItemProps, highlightedIndex, inputValue, reset } = useCombobox({
    items: results,
    itemToString: (item) => (item ? item.title : ''),
    onInputValueChange: ({ inputValue }) => {
      debouncedSearch(inputValue);
    },
    onSelectedItemChange: ({ selectedItem }) => {
      if (selectedItem) {
        onSelect?.(selectedItem);
      }
    },
  });

  return (
    <div className="relative w-full" {...getComboboxProps()}>
      <div className="relative">
        <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          {...getInputProps()}
          placeholder={placeholder}
          className="w-full bg-tm-surface border border-tm-border rounded-lg pl-10 pr-10 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
        />
        {isLoading && <div className="absolute right-10 top-1/2 -translate-y-1/2 w-5 h-5 border-2 border-t-transparent border-white rounded-full animate-spin"></div>}
        {inputValue && !isLoading && (
          <button onClick={() => reset()} className="absolute right-3 top-1/2 -translate-y-1/2">
            <ClearIcon className="h-5 w-5 text-gray-400" />
          </button>
        )}
      </div>

      <ul
        {...getMenuProps()}
        className={clsx(
          'absolute z-10 mt-1 w-full bg-tm-surface-light shadow-lg rounded-lg max-h-60 overflow-auto',
          !isOpen && 'hidden'
        )}
      >
        {isOpen && results.map((item, index) => (
          <li
            key={`${item.title}-${index}`}
            {...getItemProps({ item, index })}
            className={clsx(
              'p-3 flex items-center justify-between gap-4 cursor-pointer',
              highlightedIndex === index && 'bg-primary/20'
            )}
          >
            <div>
              <h4 className="font-semibold text-tm-text-primary">{item.title}</h4>
              <p className="text-sm text-tm-text-secondary line-clamp-1">{item.description}</p>
            </div>
            <div className="flex items-center gap-2">
              <span className={clsx('px-2 py-0.5 text-xs font-semibold text-white rounded-full', getCategoryColor(item.category))}>{item.category_display}</span>
              {onQuickAdd && (
                <button onClick={(e) => { e.stopPropagation(); onQuickAdd(item); }} className="p-2 rounded-full bg-primary text-white hover:bg-primary/80">
                  <AddIcon className="h-5 w-5" />
                </button>
              )}
            </div>
          </li>
        ))}
        {isOpen && results.length === 0 && !isLoading && (
          <li className="p-4 text-center text-tm-text-secondary">Aucun résultat</li>
        )}
      </ul>
    </div>
  );
};

export default SearchBar;
