import React, { useState, useEffect, Fragment } from "react";
import { useParams } from "react-router-dom";
import { Dialog, Transition } from "@headlessui/react";
import type { ListItem } from "../types";
import EnrichedListItem from "./EnrichedListItem";
import AppHeader from "./AppHeader";
import AppBottomNav from "./AppBottomNav";
// import clsx from 'clsx'; // non utilisé
import { FilmIcon, SeriesIcon, MusicIcon, BookIcon } from "./icons";

// --- Icônes SVG ---
const AddIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
  >
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4v16m8-8H4" />
  </svg>
);
const EditIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L15.232 5.232z"
    />
  </svg>
);
const ArrowBackIcon = ({ className }: { className?: string }) => (
  <svg
    xmlns="http://www.w3.org/2000/svg"
    className={className}
    fill="none"
    viewBox="0 0 24 24"
    stroke="currentColor"
    strokeWidth={2}
  >
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M10 19l-7-7m0 0l7-7m-7 7h18"
    />
  </svg>
);

// --- Interfaces ---
interface DashboardProps {
  onNavigate?: (section: string) => void;
}

interface TasteList {
  id: number;
  name: string;
  description: string;
  category: string;
  category_display: string;
  owner: string;
  items_count: number;
  created_at: string;
  updated_at: string;
}

// Utilisation du type ListItem global depuis types/index.ts

// --- Fonctions utilitaires ---
const getCategoryIcon = (category: string) => {
  switch (category) {
    case "FILMS":
      return <FilmIcon className="w-8 h-8 text-white" />;
    case "SERIES":
      return <SeriesIcon className="w-8 h-8 text-white" />;
    case "MUSIQUE":
      return <MusicIcon className="w-8 h-8 text-white" />;
    case "LIVRES":
      return <BookIcon className="w-8 h-8 text-white" />;
    default:
      return <FilmIcon className="w-8 h-8 text-white" />;
  }
};

const getCategoryColor = (category: string) => {
  switch (category) {
    case "FILMS":
      return "bg-red-600";
    case "SERIES":
      return "bg-blue-600";
    case "MUSIQUE":
      return "bg-green-600";
    case "LIVRES":
      return "bg-purple-600";
    default:
      return "bg-gray-600";
  }
};

const getSourceLabel = (source?: string) => {
  if (!source) return "MANUEL";

  const sourceMap: Record<string, string> = {
    tmdb: "TMDB",
    spotify: "SPOTIFY",
    openlibrary: "OPENLIB",
    google_books: "GOOGLE",
  };

  return sourceMap[source.toLowerCase()] || source.toUpperCase();
};

const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const { listId } = useParams();
  const currentListId = parseInt(listId || "1", 10);
  const [bottomNavValue, setBottomNavValue] = useState(0);
  const [list, setList] = useState<TasteList | null>(null);
  const [items, setItems] = useState<ListItem[]>([]);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [isEditingDescription, setIsEditingDescription] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [openDialog, setOpenDialog] = useState(false);
  const [editingItem, setEditingItem] = useState<ListItem | null>(null);
  const [formData, setFormData] = useState({ title: "", description: "" });
  const [submitLoading, setSubmitLoading] = useState(false);
  const [enrichingItemId, setEnrichingItemId] = useState<number | null>(null);

  // Fetch de la liste et des items
  useEffect(() => {
    const fetchListAndItems = async () => {
      try {
        setLoading(true);

        // Fetch de la liste
        const listResponse = await fetch(`/api/lists/${currentListId}/`);
        if (!listResponse.ok)
          throw new Error("Erreur lors du chargement de la liste");
        const listData = await listResponse.json();
        setList(listData);

        // Fetch des items de la liste
        const itemsResponse = await fetch(`/api/lists/${currentListId}/items/`);
        if (!itemsResponse.ok)
          throw new Error("Erreur lors du chargement des items");
        const itemsData = await itemsResponse.json();
        setItems(itemsData);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Erreur inconnue");
      } finally {
        setLoading(false);
      }
    };

    fetchListAndItems();
  }, [currentListId]);

  // Handlers pour la navigation
  const handleBottomNavChange = (
    _event: React.SyntheticEvent,
    newValue: number
  ) => {
    setBottomNavValue(newValue);
    const sections = ["listes", "explorer", "match", "social"];
    onNavigate?.(sections[newValue]);
  };

  // Handlers pour l'édition du titre
  const handleTitleEdit = async () => {
    if (!list) return;

    try {
      const response = await fetch(`/api/lists/${list.id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: list.name }),
      });

      if (!response.ok) throw new Error("Erreur lors de la sauvegarde");

      setIsEditingTitle(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erreur lors de la sauvegarde"
      );
    }
  };

  // Handlers pour l'édition de la description
  const handleDescriptionEdit = async () => {
    if (!list) return;

    try {
      const response = await fetch(`/api/lists/${list.id}/`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: list.description }),
      });

      if (!response.ok) throw new Error("Erreur lors de la sauvegarde");

      setIsEditingDescription(false);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erreur lors de la sauvegarde"
      );
    }
  };

  // Handlers pour les items
  const handleEnrichItem = async (itemId: number) => {
    if (!list) return;

    try {
      setEnrichingItemId(itemId);
      const response = await fetch(
        `/api/lists/${list.id}/items/${itemId}/enrich/`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );

      if (!response.ok) throw new Error("Erreur lors de l'enrichissement");

      // Recharger les items pour avoir les nouvelles données
      const itemsResponse = await fetch(`/api/lists/${list.id}/items/`);
      if (itemsResponse.ok) {
        const itemsData = await itemsResponse.json();
        setItems(itemsData);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erreur lors de l'enrichissement"
      );
    } finally {
      setEnrichingItemId(null);
    }
  };

  const handleEditItem = (item: ListItem) => {
    setEditingItem(item);
    setFormData({ title: item.title, description: item.description || "" });
    setOpenDialog(true);
  };

  const handleDeleteItem = async (itemId: number) => {
    if (!list || !confirm("Êtes-vous sûr de vouloir supprimer cet élément ?"))
      return;

    try {
      const response = await fetch(`/api/lists/${list.id}/items/${itemId}/`, {
        method: "DELETE",
      });

      if (!response.ok) throw new Error("Erreur lors de la suppression");

      // Mettre à jour la liste locale
      setItems(items.filter((item) => item.id !== itemId));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erreur lors de la suppression"
      );
    }
  };

  // Handlers pour le dialog
  const handleOpenDialog = () => {
    setEditingItem(null);
    setFormData({ title: "", description: "" });
    setError("");
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingItem(null);
    setFormData({ title: "", description: "" });
    setError("");
  };

  const handleSubmitItem = async () => {
    if (!formData.title.trim()) {
      setError("Le titre est requis");
      return;
    }

    try {
      setSubmitLoading(true);
      setError("");

      if (editingItem) {
        // Modification d'un item existant
        const response = await fetch(
          `/api/lists/${list!.id}/items/${editingItem.id}/`,
          {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
          }
        );

        if (!response.ok) throw new Error("Erreur lors de la modification");

        // Mettre à jour la liste locale
        setItems(
          items.map((item) =>
            item.id === editingItem.id
              ? {
                  ...item,
                  title: formData.title,
                  description: formData.description,
                }
              : item
          )
        );
      } else {
        // Création d'un nouvel item
        const response = await fetch(`/api/lists/${list!.id}/items/`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData),
        });

        if (!response.ok) throw new Error("Erreur lors de la création");

        const newItem = await response.json();
        setItems([...items, newItem]);
      }

      handleCloseDialog();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Erreur lors de la sauvegarde"
      );
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-tm-surface">
      <AppHeader title="TasteMatch" onBack={() => onNavigate?.("listes")} />

      <main className="flex-grow overflow-auto p-4 pb-20">
        <div className="max-w-2xl mx-auto bg-tm-surface-light p-4 sm:p-6 rounded-lg shadow-lg">
          <div className="flex items-center mb-4">
            <button
              onClick={() => onNavigate?.("listes")}
              className="flex items-center text-sm text-tm-text-secondary hover:text-tm-text-primary"
            >
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
                value={list?.name || ""}
                onChange={(e) =>
                  setList(list ? { ...list, name: e.target.value } : null)
                }
                onBlur={handleTitleEdit}
                onKeyPress={(e) => e.key === "Enter" && handleTitleEdit()}
                className="text-2xl sm:text-3xl font-bold bg-transparent border-b-2 border-primary w-full focus:outline-none"
                autoFocus
              />
            ) : (
              <div className="flex items-center">
                <h1 className="text-2xl sm:text-3xl font-bold text-tm-text-primary flex-grow">
                  {list?.name || "Liste de goûts"}
                </h1>
                <button
                  onClick={() => setIsEditingTitle(true)}
                  className="p-2 rounded-full hover:bg-white/10"
                >
                  <EditIcon className="h-5 w-5 text-tm-text-secondary" />
                </button>
              </div>
            )}
          </div>

          {list?.category_display && (
            <p className="text-md text-primary font-semibold mb-4">
              📂 {list.category_display}
            </p>
          )}

          <div className="mb-6">
            {loading ? (
              <div className="h-6 bg-gray-700 rounded w-1/2 animate-pulse"></div>
            ) : isEditingDescription ? (
              <textarea
                value={list?.description || ""}
                onChange={(e) =>
                  setList(
                    list ? { ...list, description: e.target.value } : null
                  )
                }
                onBlur={handleDescriptionEdit}
                onKeyPress={(e) => e.key === "Enter" && handleDescriptionEdit()}
                className="text-sm text-tm-text-secondary bg-transparent border-b-2 border-primary w-full focus:outline-none resize-none"
                rows={2}
                autoFocus
              />
            ) : (
              <div className="flex items-start">
                <p className="text-sm text-tm-text-secondary flex-grow">
                  {list?.description || "Aucune description"}
                </p>
                <button
                  onClick={() => setIsEditingDescription(true)}
                  className="p-1 rounded-full hover:bg-white/10 ml-2"
                >
                  <EditIcon className="h-4 w-4 text-tm-text-secondary" />
                </button>
              </div>
            )}
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          <h2 className="text-xl font-semibold mb-4">
            Éléments ({items.length})
          </h2>

          {loading ? (
            <div className="flex justify-center py-8">{/* Spinner SVG */}</div>
          ) : items.length === 0 ? (
            <div className="text-center py-8 text-tm-text-secondary">
              <p>Cette liste est vide.</p>
              <p>Ajoutez votre premier élément !</p>
            </div>
          ) : (
            <div className="space-y-2">
              {items.map((item) => (
                <EnrichedListItem
                  key={item.id}
                  external_ref={item.external_ref}
                  title={item.title}
                  position={item.position}
                  description={item.description}
                  onEnrich={() => handleEnrichItem(item.id)}
                  isEnriching={enrichingItemId === item.id}
                  onEdit={() => handleEditItem(item)}
                  onDelete={() => handleDeleteItem(item.id)}
                  getCategoryIcon={() =>
                    getCategoryIcon(list?.category || "FILMS")
                  }
                  getCategoryColor={() =>
                    getCategoryColor(list?.category || "FILMS")
                  }
                  getSourceLabel={getSourceLabel}
                />
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
                    {editingItem ? "Modifier l'élément" : "Ajouter un élément"}
                  </Dialog.Title>
                  <div className="mt-4">
                    <input
                      type="text"
                      placeholder="Titre *"
                      value={formData.title}
                      onChange={(e) =>
                        setFormData({ ...formData, title: e.target.value })
                      }
                      className="w-full bg-tm-surface px-4 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-primary mb-4"
                    />
                    <textarea
                      placeholder="Description (optionnelle)"
                      value={formData.description}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          description: e.target.value,
                        })
                      }
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
                      {submitLoading
                        ? "Sauvegarde..."
                        : editingItem
                        ? "Modifier"
                        : "Ajouter"}
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
