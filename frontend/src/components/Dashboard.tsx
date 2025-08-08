import React, { useState, useEffect, Fragment } from 'react';
import { useParams } from 'react-router-dom';
import { Dialog, Transition } from '@headlessui/react';
import EnrichedListItem from './EnrichedListItem';
import AppHeader from './AppHeader';
import AppBottomNav from './AppBottomNav';
import clsx from 'clsx';

// --- Icônes SVG ---
const AddIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
  </svg>
);
const EditIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L15.232 5.232z" />
  </svg>
);
const ArrowBackIcon = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
  </svg>
);

// --- Interfaces ---
interface DashboardProps {
  onNavigate?: (section: string) => void;
}

interface TasteList { /* ... */ }
interface ListItem { /* ... */ }

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { listId } = useParams();
  const currentListId = parseInt(listId || '1', 10);
  const [bottomNavValue, setBottomNavValue] = useState(0);
  const [list, setList] = useState<TasteList | null>(null);
  const [items, setItems] = useState<ListItem[]>([]);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<ListItem | null>(null);
  const [formData, setFormData] = useState({ title: '', description: '' });
  const [submitLoading, setSubmitLoading] = useState(false);
  const [enrichingItemId, setEnrichingItemId] = useState<number | null>(null);

  // ... (logique de fetch et de handlers reste la même)

  return (
    <div className="flex flex-col h-screen bg-tm-surface">
      <AppHeader title="TasteMatch" onBack={() => onNavigate?.('listes')} />

      <main className="flex-grow overflow-auto p-4 pb-20">
        <div className="max-w-2xl mx-auto bg-tm-surface-light p-4 sm:p-6 rounded-lg shadow-lg">
          
          <div className="flex items-center mb-4">
            <button onClick={() => onNavigate?.('listes')} className="flex items-center text-sm text-tm-text-secondary hover:text-tm-text-primary">
              <ArrowBackIcon className="h-5 w-5 mr-2" />
              Retour aux Collections
            </button>
          </div>

          <div className="mb-4">
            {loading ? (
              <div className="h-9 bg-gray-700 rounded w-3/4 animate-pulse"></div>
            ) : isEditingTitle ? (
              <input
                type="text"
                value={list?.name || ''}
                onChange={(e) => setList(list ? { ...list, name: e.target.value } : null)}
                onBlur={() => { /* ... */ }}
                onKeyPress={(e) => { /* ... */ }}
                className="text-2xl sm:text-3xl font-bold bg-transparent border-b-2 border-primary w-full focus:outline-none"
                autoFocus
              />
            ) : (
              <div className="flex items-center">
                <h1 className="text-2xl sm:text-3xl font-bold text-tm-text-primary flex-grow">
                  {list?.name || 'Liste de goûts'}
                </h1>
                <button onClick={() => setIsEditingTitle(true)} className="p-2 rounded-full hover:bg-white/10">
                  <EditIcon className="h-5 w-5 text-tm-text-secondary" />
                </button>
              </div>
            )}
          </div>

          {list?.category_display && (
            <p className="text-md text-primary font-semibold mb-4">📂 {list.category_display}</p>
          )}

          <div className="mb-6">
            {loading ? (
              <div className="h-5 bg-gray-700 rounded w-full animate-pulse"></div>
            ) : isEditingDescription ? (
              <textarea
                value={list?.description || ''}
                onChange={(e) => setList(list ? { ...list, description: e.target.value } : null)}
                onBlur={() => { /* ... */ }}
                className="text-tm-text-secondary bg-transparent border-b-2 border-primary w-full focus:outline-none"
                autoFocus
              />
            ) : (
              <div className="flex items-start">
                <p className="text-tm-text-secondary flex-grow">
                  {list?.description || 'Cliquez pour ajouter une description.'}
                </p>
                <button onClick={() => setIsEditingDescription(true)} className="p-2 rounded-full hover:bg-white/10">
                  <EditIcon className="h-5 w-5 text-tm-text-secondary" />
                </button>
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          <h2 className="text-xl font-semibold mb-4">Éléments ({items.length})</h2>

          {loading ? (
            <div className="flex justify-center py-8">
              {/* Spinner SVG */}
            </div>
          ) : items.length === 0 ? (
            <div className="text-center py-8 text-tm-text-secondary">
              <p>Cette liste est vide.</p>
              <p>Ajoutez votre premier élément !</p>
            </div>
          ) : (
            <div className="space-y-2">
              {items.map((item, index) => (
                <EnrichedListItem key={item.id} /* ...props */ />
              ))}
            </div>
          )}

          <div className="mt-6">
            <button
              onClick={() => handleOpenDialog()}
              className="w-full flex items-center justify-center gap-2 border-2 border-tm-border hover:bg-primary hover:border-primary transition-colors text-tm-text-primary font-semibold py-3 rounded-lg"
            >
              <AddIcon className="h-6 w-6" />
              Ajouter un élément
            </button>
          </div>
        </div>
      </main>

      <AppBottomNav value={bottomNavValue} onChange={handleBottomNavChange} />

      {/* --- Dialog Headless UI --- */}
      <Transition appear show={openDialog} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={handleCloseDialog}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-50" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-md transform overflow-hidden rounded-2xl bg-tm-surface-light p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-lg font-medium leading-6 text-tm-text-primary"
                  >
                    {editingItem ? 'Modifier l\'élément' : 'Ajouter un élément'}
                  </Dialog.Title>
                  <div className="mt-4">
                    <input
                      type="text"
                      placeholder="Titre *"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      className="w-full bg-tm-surface px-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-primary mb-4"
                    />
                    <textarea
                      placeholder="Description (optionnelle)"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      rows={4}
                      className="w-full bg-tm-surface px-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  {error && (
                    <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg my-4 text-sm">
                      {error}
                    </div>
                  )}

                  <div className="mt-6 flex justify-end gap-4">
                    <button
                      type="button"
                      className="inline-flex justify-center rounded-md border border-transparent bg-tm-surface px-4 py-2 text-sm font-medium text-tm-text-secondary hover:bg-tm-surface/80 focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                      onClick={handleCloseDialog}
                    >
                      Annuler
                    </button>
                    <button
                      type="button"
                      disabled={submitLoading}
                      className="inline-flex justify-center rounded-md border border-transparent bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/80 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:bg-gray-500"
                      onClick={handleSubmitItem}
                    >
                      {submitLoading ? 'Sauvegarde...' : (editingItem ? 'Modifier' : 'Ajouter')}
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </div>
  );
};

export default Dashboard;