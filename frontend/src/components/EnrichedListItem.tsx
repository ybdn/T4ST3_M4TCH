import React, { useState, Fragment } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import clsx from 'clsx';

// --- Icônes SVG ---
const EditIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L15.232 5.232z" /></svg> );
const DeleteIcon = ({ className }: { className?: string }) => ( <svg xmlns="http://www.w3.org/2000/svg" className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}><path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg> );
const RefreshIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
    aria-hidden="true"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M4 4v5h5M20 20v-5h-5M4 4l1.5 1.5A9 9 0 0120.5 15M20 20l-1.5-1.5A9 9 0 003.5 9"
    />
  </svg>
);

const OpenInNewIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
    aria-hidden="true"
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
    />
  </svg>
);

// Les icônes suivantes ne sont pas utilisées dans le composant et peuvent être supprimées pour corriger les erreurs de lint.
//// const MovieIcon = ({ className }: { className?: string }) => ( ... );
//// const TvIcon = ({ className }: { className?: string }) => ( ... );
//// const MusicNoteIcon = ({ className }: { className?: string }) => ( ... );
//// const BookIcon = ({ className }: { className?: string }) => ( ... );

// --- Types ---
type ExternalReference = {
  poster_url?: string;
  source?: string;
  metadata?: {
    genres?: string[];
    backdrop_url?: string;
    [key: string]: unknown;
  };
  // Ajoutez d'autres propriétés si nécessaire
};

interface EnrichedListItemProps {
  external_ref?: ExternalReference;
  title: string;
  position: number;
  description?: string;
  onEnrich?: () => void;
  isEnriching?: boolean;
  onEdit?: () => void;
  onDelete?: () => void;
  getCategoryIcon: () => React.ReactNode;
  getCategoryColor: () => string;
  getSourceLabel: (source?: string) => string;
}

const EnrichedListItem: React.FC<EnrichedListItemProps> = ({
  external_ref,
  title,
  position,
  description,
  onEnrich,
  isEnriching,
  onEdit,
  onDelete,
  getCategoryIcon,
  getCategoryColor,
  getSourceLabel,
}) => {
  const [imageError, setImageError] = useState(false);
  const [detailsOpen, setDetailsOpen] = useState(false);

  // ... (logique getCategoryIcon, getSourceLabel, etc. reste la même)

  return (
    <>
      <div className="flex bg-tm-surface-light rounded-lg shadow-md mb-4 transition-transform duration-200 hover:-translate-y-0.5 hover:shadow-xl">
        {/* Image/Poster */}
        <div className="relative flex-shrink-0 w-20 sm:w-32">
          {external_ref?.poster_url && !imageError ? (
            <img
              src={external_ref.poster_url}
              alt={title}
              className="w-full h-32 sm:h-48 object-cover rounded-l-lg"
              onError={() => setImageError(true)}
            />
          ) : (
            <div className={clsx('w-full h-32 sm:h-48 flex items-center justify-center rounded-l-lg', getCategoryColor())}>
              {getCategoryIcon()}
            </div>
          )}
          <div className="absolute top-2 left-2 bg-primary text-white w-6 h-6 flex items-center justify-center text-xs font-bold rounded-full">
            {position}
          </div>
          {external_ref && (
            <div className="absolute bottom-1 left-1 bg-green-600 text-white px-1.5 py-0.5 text-xs font-bold rounded">
              {getSourceLabel(external_ref.source)}
            </div>
          )}
        </div>

        {/* Contenu */}
        <div className="flex-1 p-3 relative flex flex-col">
          <div className="flex justify-between items-start mb-1">
            <h3 className="text-md sm:text-lg font-semibold text-tm-text-primary mr-2 leading-tight">
              {title}
            </h3>
            <div className="flex gap-1">
              {onEnrich && (
                <button onClick={onEnrich} disabled={isEnriching} className="p-1 rounded-full hover:bg-white/10 text-primary">
                  {isEnriching ? <div className="w-4 h-4 border-2 border-t-transparent border-white rounded-full animate-spin"></div> : <RefreshIcon className="h-5 w-5" />}
                </button>
              )}
              {onEdit && (
                <button onClick={onEdit} className="p-1 rounded-full hover:bg-white/10 text-primary">
                  <EditIcon className="h-5 w-5" />
                </button>
              )}
              {onDelete && (
                <button onClick={onDelete} className="p-1 rounded-full hover:bg-white/10 text-red-500">
                  <DeleteIcon className="h-5 w-5" />
                </button>
              )}
            </div>
          </div>

          {external_ref && (
            <div className="flex items-center gap-2 mb-2 text-xs text-tm-text-secondary">
              {/* ... (Rating and Release Date) ... */}
            </div>
          )}

          <p className="text-xs sm:text-sm text-tm-text-secondary leading-snug line-clamp-2 sm:line-clamp-3 flex-grow">
            {description}
          </p>

          {external_ref?.metadata && (
            <div className="mt-auto pt-2">
              <div className="flex flex-wrap gap-1 mb-1">
                {external_ref.metadata.genres?.slice(0, 3).map((genre: string) => (
                  <span key={genre} className="px-2 py-0.5 text-xs bg-tm-surface rounded-full">{genre}</span>
                ))}
              </div>
              <button onClick={() => setDetailsOpen(true)} className="flex items-center gap-1 text-xs text-primary hover:underline">
                <OpenInNewIcon className="h-4 w-4" />
                Voir détails
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Modale de détails */}
      <Transition appear show={detailsOpen} as={Fragment}>
        <Dialog as="div" className="relative z-50" onClose={() => setDetailsOpen(false)}>
          <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0" enterTo="opacity-100" leave="ease-in duration-200" leaveFrom="opacity-100" leaveTo="opacity-0">
            <div className="fixed inset-0 bg-black bg-opacity-60" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4 text-center">
              <Transition.Child as={Fragment} enter="ease-out duration-300" enterFrom="opacity-0 scale-95" enterTo="opacity-100 scale-100" leave="ease-in duration-200" leaveFrom="opacity-100 scale-100" leaveTo="opacity-0 scale-95">
                <Dialog.Panel className="w-full max-w-lg transform overflow-hidden rounded-2xl bg-tm-surface-light p-6 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-tm-text-primary flex items-center gap-2">
                    {getCategoryIcon()}
                    {title}
                    {external_ref && <span className="px-2 py-0.5 text-xs font-semibold bg-primary text-white rounded-full">{getSourceLabel(external_ref.source)}</span>}
                  </Dialog.Title>
                  
                  <div className="mt-4">
                    {external_ref?.metadata?.backdrop_url && !imageError && (
                      <img src={external_ref.metadata.backdrop_url} alt={`${title} backdrop`} className="w-full h-48 object-cover rounded-lg mb-4" onError={() => setImageError(true)} />
                    )}
                    <p className="text-sm text-tm-text-secondary">
                      {description}
                    </p>
                    {/* {renderMetadataDetails()} */}
                  </div>

                  <div className="mt-4 flex justify-end">
                    <button type="button" className="inline-flex justify-center rounded-md border border-transparent bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/80 focus:outline-none" onClick={() => setDetailsOpen(false)}>
                      Fermer
                    </button>
                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </>
  );
};

export default EnrichedListItem;
