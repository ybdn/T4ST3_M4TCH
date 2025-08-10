# Endpoint Match Action `/api/match/action/`

Permet d'enregistrer une action utilisateur (like, dislike, add, skip) sur un contenu recommandé.

## Objectif

- Centraliser les interactions utilisateur pour futures fonctionnalités (compatibilité, suggestions sociales, analytics).
- Garantir l'idempotence (pas de doublons de préférences).

## Authentification

JWT obligatoire (`Authorization: Bearer <token>`).

## Méthode

`POST /api/match/action/`

## Payload

```json
{
  "external_id": "fb_movie_001",
  "source": "tmdb",
  "category": "FILMS",
  "action": "like",
  "title": "Inception",
  "metadata": { "popularity": 80 },
  "description": "Thriller SF"
}
```

Alias acceptés / normalisation:

- `category` ou `content_type`
- Actions: `like|liked`, `dislike|disliked`, `add|added`, `skip|skipped`

## Réponse (201)

```json
{
  "success": true,
  "action": "liked",
  "preference_id": 123,
  "updated": false,
  "list_id": 5,
  "list_item_id": 42
}
```

Champs `list_id` / `list_item_id` présents uniquement si action finale == `added`.

## Codes d'erreur

| Code | Raison                           | Exemple                   |
| ---- | -------------------------------- | ------------------------- |
| 400  | Action invalide / champ manquant | `{ "action": "explode" }` |
| 401  | Non authentifié                  | Absence header Bearer     |
| 500  | Erreur interne inattendue        | Exception non prévue      |

## Règles métier

1. Idempotence stricte: répéter la même action retourne le même `preference_id` et `updated=false`.
2. Changement d'action (like -> add, dislike -> like, etc.) met à jour la préférence (`updated=true`).
3. Passage vers `added` insère l'item dans la liste catégorie de l'utilisateur (créée si nécessaire) avec position suivante UNIQUEMENT si création directe ou transition depuis une autre action (add répété => aucune duplication).
4. Enrichissement externe asynchrone (best-effort) — échec d'enrichissement n'annule pas la création.
5. Les actions ignorées (`skip|skipped`) sont validées mais ne créent pas d'élément de liste.
6. Statistiques profil:

- `total_matches` n'augmente qu'à la première interaction avec un contenu donné.
- `successful_matches` n'augmente que lors d'un passage vers `added` (création en `added` ou transition). Répéter `added` ensuite n'incrémente plus.

## Tests principaux

- Succès like
- Idempotence like -> like
- Changement like -> add (updated=true)
- Idempotence add -> add (pas de second updated ni second list item)
- Action invalide -> 400
- Statistiques: total_matches idempotent
- Statistiques: successful_matches uniquement sur passage vers added

## Évolutions futures possibles

- Rate limiting par utilisateur sur actions/minute.
- Historisation (journal des changements d'action).
- WebSocket / SSE pour retour temps réel dans une session de match.
- Score de compatibilité recalculé à chaud.
