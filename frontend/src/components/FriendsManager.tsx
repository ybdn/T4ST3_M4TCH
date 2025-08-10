/**
 * Composant pour gérer les amis et les demandes d'amitié
 */

import React, { useState } from "react";
import { Tab, TabGroup, TabList, TabPanel, TabPanels } from "@headlessui/react";
import { useFriends, useFriendSearch } from "../hooks";
// Types sociaux désactivés : utilisation de types minimaux
type FriendUser = {
  user_id?: number;
  display_name: string;
  gamertag: string;
  avatar_url?: string;
};
import clsx from "clsx";

interface FriendsManagerProps {
  onClose?: () => void;
  onSelectFriend?: (friend: FriendUser) => void;
}

const FriendsManager: React.FC<FriendsManagerProps> = ({
  onClose,
  onSelectFriend,
}) => {
  const { friends, loading, error } = useFriends();

  const { addingFriend } = useFriendSearch();

  const [selectedTab, setSelectedTab] = useState(0);
  const [searchGamertag, setSearchGamertag] = useState("");
  const [searchSuccess, setSearchSuccess] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchGamertag.trim()) return;
    setSearchSuccess(`(stub) Demande envoyée à ${searchGamertag}`);
    setSearchGamertag("");
  };

  // Features demandes d'amis désactivées

  const FriendCard: React.FC<{
    friend: FriendUser & { compatibility_score?: number };
    showActions?: boolean;
  }> = ({ friend, showActions = false }) => (
    <div className="tm-glass p-4 rounded-lg flex items-center space-x-3">
      {/* Avatar */}
      <div className="w-12 h-12">
        {friend.avatar_url ? (
          <img
            src={friend.avatar_url}
            alt={friend.display_name}
            className="w-full h-full rounded-full object-cover"
          />
        ) : (
          <div className="w-full h-full rounded-full bg-tm-primary flex items-center justify-center">
            <span className="text-lg font-bold text-white">
              {friend.display_name.charAt(0).toUpperCase()}
            </span>
          </div>
        )}
      </div>

      {/* Informations */}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-white truncate">
          {friend.display_name}
        </h3>
        <p className="text-sm text-tm-text-muted">#{friend.gamertag}</p>
        {typeof friend.compatibility_score === "number" && (
          <div className="text-xs text-tm-text-muted mt-0.5">
            Compatibilité:{" "}
            <span className="text-tm-primary font-semibold">
              {friend.compatibility_score}%
            </span>
          </div>
        )}
      </div>

      {/* Actions */}
      {showActions && onSelectFriend && (
        <button
          onClick={() => onSelectFriend(friend)}
          className="px-3 py-1 bg-tm-primary text-white text-sm rounded-lg hover:bg-tm-primary-700 transition-colors"
        >
          Défier
        </button>
      )}
    </div>
  );

  // RequestCard supprimé

  return (
    <div className="tm-glass-card rounded-xl p-6 max-h-[80vh] overflow-y-auto">
      {/* En-tête */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-white">Amis</h2>
        {onClose && (
          <button
            onClick={onClose}
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
        )}
      </div>

      {/* Onglets */}
      <TabGroup selectedIndex={selectedTab} onChange={setSelectedTab}>
        <TabList className="flex space-x-1 bg-white/5 p-1 rounded-lg mb-6">
          <Tab
            className={({ selected }) =>
              clsx(
                "w-full rounded-lg py-2.5 text-sm font-medium leading-5 transition-all duration-200",
                "ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2",
                selected
                  ? "bg-white text-tm-bg shadow"
                  : "text-tm-text hover:bg-white/10 hover:text-white"
              )
            }
          >
            Mes Amis ({friends.length})
          </Tab>
          {/* Onglet demandes retiré */}
          <Tab
            className={({ selected }) =>
              clsx(
                "w-full rounded-lg py-2.5 text-sm font-medium leading-5 transition-all duration-200",
                "ring-white ring-opacity-60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2",
                selected
                  ? "bg-white text-tm-bg shadow"
                  : "text-tm-text hover:bg-white/10 hover:text-white"
              )
            }
          >
            Ajouter
          </Tab>
        </TabList>

        <TabPanels className="space-y-4">
          {/* Panel Mes Amis */}
          <TabPanel>
            {loading && friends.length === 0 ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div
                    key={i}
                    className="animate-pulse tm-glass p-4 rounded-lg flex items-center space-x-3"
                  >
                    <div className="w-12 h-12 bg-white/20 rounded-full"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-white/20 rounded w-3/4"></div>
                      <div className="h-3 bg-white/20 rounded w-1/2"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : friends.length > 0 ? (
              <div className="space-y-3">
                {(friends as FriendUser[]).map((friend) => (
                  <FriendCard
                    key={friend.user_id || friend.gamertag}
                    friend={friend as FriendUser}
                    showActions={!!onSelectFriend}
                  />
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-6xl mb-4">👥</div>
                <p className="text-tm-text mb-2">Aucun ami pour le moment</p>
                <p className="text-tm-text-muted text-sm">
                  Ajoutez des amis avec leur gamertag !
                </p>
              </div>
            )}
          </TabPanel>

          {/* Panel demandes retiré */}

          {/* Panel Ajouter un ami */}
          <TabPanel>
            <div className="space-y-4">
              {/* Formulaire de recherche */}
              <form onSubmit={handleSearch} className="space-y-4">
                <div>
                  <label
                    htmlFor="gamertag"
                    className="block text-sm font-medium text-tm-text mb-2"
                  >
                    Gamertag de votre ami
                  </label>
                  <input
                    type="text"
                    id="gamertag"
                    value={searchGamertag}
                    onChange={(e) => setSearchGamertag(e.target.value)}
                    className="w-full px-3 py-2 tm-glass-input rounded-lg text-white placeholder-tm-text-muted focus:outline-none focus:ring-2 focus:ring-tm-primary"
                    placeholder="TM_XXXX"
                    disabled={addingFriend}
                  />
                  <p className="text-xs text-tm-text-muted mt-1">
                    Format: TM_XXXX (ex: TM_ABCD)
                  </p>
                </div>

                <button
                  type="submit"
                  className="w-full py-2 px-4 bg-tm-primary text-white rounded-lg hover:bg-tm-primary-700 transition-colors disabled:opacity-50"
                  disabled={addingFriend || !searchGamertag.trim()}
                >
                  {addingFriend ? (
                    <div className="flex items-center justify-center">
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Recherche...
                    </div>
                  ) : (
                    "Envoyer une demande"
                  )}
                </button>
              </form>

              {/* Messages de feedback */}
              {searchSuccess && (
                <div className="p-3 bg-green-500/20 border border-green-500/30 rounded-lg">
                  <p className="text-green-200 text-sm">{searchSuccess}</p>
                </div>
              )}

              {/* Instructions */}
              <div className="p-4 tm-glass rounded-lg">
                <h3 className="font-semibold text-white mb-2">
                  Comment ajouter un ami ?
                </h3>
                <ul className="text-sm text-tm-text-muted space-y-1">
                  <li>• Demandez son gamertag à votre ami</li>
                  <li>• Saisissez-le dans le champ ci-dessus</li>
                  <li>• Il recevra une demande d'amitié</li>
                  <li>• Une fois acceptée, vous pourrez jouer ensemble !</li>
                </ul>
              </div>
            </div>
          </TabPanel>
        </TabPanels>
      </TabGroup>

      {/* Erreur globale */}
      {error && (
        <div className="mt-4 p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
          <p className="text-red-200 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
};

export default FriendsManager;
