import React, { useState, Fragment } from 'react';
import { Tab, Listbox, Transition } from '@headlessui/react';
import SearchBar from '../components/SearchBar';
import SuggestionCards from '../components/SuggestionCards';
import ExternalSearchResults from '../components/ExternalSearchResults';
import ExternalSearchBar from '../components/ExternalSearchBar';
import AppHeader from '../components/AppHeader';
import AppBottomNav from '../components/AppBottomNav';
import { useFeedback } from '../context/FeedbackContext';
import clsx from 'clsx';

// --- Icônes SVG ---
const AddIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" /></svg> );
const SearchIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg> );
const LanguageIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M3 5h12M9 3v2m4 13-4-4-4 4M1 11h14M12 11a2 2 0 100-4 2 2 0 000 4z" /></svg> );

// --- Interfaces ---
interface QuickAddPageProps { /* ... */ }

const QuickAddPage: React.FC<QuickAddPageProps> = ({ onNavigate }) => {
  // ... (logique de gestion d'état reste la même)

  return (
    <div className="flex flex-col h-screen bg-tm-surface text-tm-text-primary">
      <AppHeader title="T4ST3 M4TCH" />

      <main className="flex-grow p-4 overflow-auto pb-20">
        <div className="max-w-2xl mx-auto bg-tm-surface-light p-4 sm:p-6 rounded-lg shadow-lg">
          <h1 className="text-2xl sm:text-3xl font-bold text-tm-text-primary mb-4">Ajout Rapide</h1>
          
          <Listbox value={selectedCategory} onChange={setSelectedCategory}>
            <div className="relative mt-1 mb-4">
              <Listbox.Button className="relative w-full cursor-default rounded-lg bg-tm-surface py-3 pl-3 pr-10 text-left shadow-md focus:outline-none focus-visible:border-indigo-500 focus-visible:ring-2 focus-visible:ring-white/75 focus-visible:ring-offset-2 focus-visible:ring-offset-orange-300 sm:text-sm">
                <span className="block truncate">{getSelectedCategoryConfig().label}</span>
                <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">{/* Chevron Icon */}</span>
              </Listbox.Button>
              <Transition as={Fragment} leave="transition ease-in duration-100" leaveFrom="opacity-100" leaveTo="opacity-0">
                <Listbox.Options className="absolute mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black/5 focus:outline-none sm:text-sm">
                  {categories.map((category, categoryIdx) => (
                    <Listbox.Option key={categoryIdx} className={({ active }) => `relative cursor-default select-none py-2 pl-10 pr-4 ${active ? 'bg-amber-100 text-amber-900' : 'text-gray-900'}`} value={category.value}>
                      {({ selected }) => (
                        <><span className={`block truncate ${selected ? 'font-medium' : 'font-normal'}`}>{category.label}</span>{selected ? <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-amber-600">{/* Check Icon */}</span> : null}</>
                      )}
                    </Listbox.Option>
                  ))}
                </Listbox.Options>
              </Transition>
            </div>
          </Listbox>

          <Tab.Group>
            <Tab.List className="flex space-x-1 rounded-xl bg-tm-surface p-1">
              {/* ... Tab buttons ... */}
            </Tab.List>
            <Tab.Panels className="mt-4">
              <Tab.Panel> 
                <SearchBar category={selectedCategory === 'ALL' ? undefined : selectedCategory} onSelect={handleSearchSelect} onQuickAdd={handleSearchSelect} />
              </Tab.Panel>
              <Tab.Panel>
                <SuggestionCards category={selectedCategory === 'ALL' ? undefined : selectedCategory} onAdd={handleSuggestionAdd} />
              </Tab.Panel>
              <Tab.Panel>
                <ExternalSearchBar category={selectedCategory === 'ALL' ? undefined : selectedCategory} onSelect={handleExternalResultSelect} onQuickAdd={handleExternalResultAdd} onQueryChange={setExternalQuery} showSourceFilter />
                <div className="mt-4">
                  <ExternalSearchResults query={externalQuery} category={selectedCategory === 'ALL' ? undefined : selectedCategory} onAdd={handleExternalResultAdd} onSelect={handleExternalResultSelect} />
                </div>
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>
        </div>
      </main>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />
    </div>
  );
};

export default QuickAddPage;
