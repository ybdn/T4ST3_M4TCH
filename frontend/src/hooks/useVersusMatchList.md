# useVersusMatchList Hook

Ce hook permet de récupérer la liste des matchs de goûts entre utilisateurs.

## Usage

```typescript
import { useVersusMatchList } from '../hooks/useVersusMatchList';

function MyComponent() {
  const { matches, loading, error, total, refresh } = useVersusMatchList({
    status: 'active', // Optionnel: 'active', 'finished', 'cancelled'
    category: 'FILMS', // Optionnel: 'FILMS', 'SERIES', 'MUSIQUE', 'LIVRES'
    limit: 10, // Optionnel: nombre max de résultats (défaut: 20)
  });

  if (loading) return <div>Chargement...</div>;
  if (error) return <div>Erreur: {error}</div>;

  return (
    <div>
      <h2>Matchs ({total})</h2>
      <button onClick={refresh}>Actualiser</button>
      {matches.map(match => (
        <div key={match.id}>
          <h3>{match.other_user?.username}</h3>
          <p>Score: {match.compatibility_score}%</p>
          <p>Statut: {match.status_display}</p>
          <p>Catégorie: {match.category_display}</p>
        </div>
      ))}
    </div>
  );
}
```

## Interface VersusMatch

```typescript
interface VersusMatch {
  id: number;
  user1: number;
  user2: number;
  user1_username: string;
  user2_username: string;
  status: 'active' | 'finished' | 'cancelled';
  status_display: string;
  compatibility_score: number | null;
  category: string | null;
  category_display: string | null;
  other_user: {
    id: number;
    username: string;
  } | null;
  created_at: string;
  updated_at: string;
  finished_at: string | null;
}
```

## Fonctionnalités

- ✅ Récupère les matchs actifs et terminés
- ✅ Tri par date de mise à jour descendante
- ✅ Limitation à 20 résultats maximum
- ✅ Filtrage par statut et catégorie
- ✅ Gestion des erreurs et états de chargement
- ✅ Fonction de rafraîchissement
- ✅ Compatible avec l'authentification JWT

## API Backend

L'endpoint correspondant : `GET /api/versus-matches/`

Paramètres de requête :
- `status`: filtre par statut
- `category`: filtre par catégorie  
- `limit`: nombre max de résultats (max 20)