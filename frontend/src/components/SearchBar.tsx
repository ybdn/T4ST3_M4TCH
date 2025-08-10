import React, { useState } from "react";

// Stub très simplifié. L'implémentation complète sera réintroduite après stabilisation build.

interface SearchResult {
  title: string;
  description?: string;
  category?: string;
  category_display?: string;
}

interface SearchBarProps {
  placeholder?: string;
  onSelect?: (item: SearchResult) => void;
  onQuickAdd?: (item: SearchResult) => void;
}

//const dummyResults: SearchResult[] = [];

const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = "Recherche désactivée (refactor en cours)",
}) => {
  const [value, setValue] = useState("");
  const showDropdown = false; // désactivé pour le moment
  return (
    <div className="relative w-full opacity-70">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled
        placeholder={placeholder}
        className="w-full bg-tm-surface border border-tm-border rounded-lg pl-4 pr-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60"
      />
      {showDropdown && (
        <div className="absolute z-10 mt-1 w-full bg-tm-surface-light rounded-lg shadow-lg p-4 text-sm text-tm-text-secondary">
          (Aucun résultat)
        </div>
      )}
    </div>
  );
};

export default SearchBar;
