import React from 'react';
import { useVersusMatchList } from '../hooks/useVersusMatchList';

// Test component to verify the hook works
const VersusMatchListTest: React.FC = () => {
  const { matches, loading, error, total, refresh } = useVersusMatchList();

  if (loading) {
    return <div className="p-4">Chargement des matchs...</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 text-red-700 rounded">
        Erreur: {error}
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Matchs Versus ({total})</h2>
        <button
          onClick={refresh}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Actualiser
        </button>
      </div>
      
      {matches.length === 0 ? (
        <p>Aucun match trouvé.</p>
      ) : (
        <div className="space-y-3">
          {matches.map((match) => (
            <div key={match.id} className="p-4 border rounded-lg">
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="font-semibold">
                    {match.other_user?.username || 'Utilisateur inconnu'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {match.category_display || 'Toutes catégories'}
                  </p>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold">
                    {match.compatibility_score?.toFixed(1) || 'N/A'}%
                  </div>
                  <div className={`text-sm px-2 py-1 rounded ${
                    match.status === 'active' ? 'bg-green-100 text-green-700' :
                    match.status === 'finished' ? 'bg-gray-100 text-gray-700' :
                    'bg-red-100 text-red-700'
                  }`}>
                    {match.status_display}
                  </div>
                </div>
              </div>
              <div className="mt-2 text-xs text-gray-500">
                Créé le {new Date(match.created_at).toLocaleDateString()}
                {match.updated_at !== match.created_at && (
                  <> • Mis à jour le {new Date(match.updated_at).toLocaleDateString()}</>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default VersusMatchListTest;