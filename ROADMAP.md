# T4ST3 M4TCH – Roadmap Bêta

Ce document structure la trajectoire jusqu'à la **bêta fermée**.

## Vision Bêta

Fonctionnalités utilisables par des utilisateurs réels :

- Auth (login/register) stable
- Recommandations multi‑sources (Films, Séries, Livres, Musique basique)
- Actions utilisateur (like / dislike / add) persistées
- Listes personnelles
- Profil social read‑only + stats basiques
- Amis (ajout / acceptation)
- Versus match simple (10 rounds, score, fin)
- PWA installable (offline shell minimal)
- Observabilité (logs structurés, erreurs captées)
- Sécurité minimale (rate limiting, validations)

Hors scope : temps réel, matchmaking avancé, gamification complexe, analytics fines.

## Milestones Résumées

| Code | Milestone | Objectif clé |
|------|-----------|--------------|
| M0 | Baseline Stable | Stubs & build propre (ACQUIS) |
| M1 | Core Match Alpha | Recos + actions réelles |
| M2 | Social v1 | Profil + amis basiques |
| M3 | Versus v1 | Boucle de jeu simple |
| M4 | Qualité/Obs | Tests, logs, métriques |
| M5 | Bêta Fermée | 10–50 users réels |
| M6 | Bêta Élargie | Performance & polish |

## Principes d'Architecture

- Feature flags pour activer progressivement (backend + endpoint /config + injection frontend)
- Services spécialisés (RecommendationService, CompatibilityService, VersusMatchService)
- DTO/API contract stables versionnés /api/v1
- Tracking unifié des actions (UserPreference + events loggable)
- Couche hooks front isolante vs API

## Backlog – Epics

- A: Foundation & Feature Flags
- B: Recommandations & Préférences
- C: Social Profile
- D: Friends
- E: Versus
- F: Observabilité & Qualité
- G: Sécurité / Hardening
- H: Performance
- I: PWA & UX
- J: Documentation & DevEx
- K: Lancement Bêta

## Top 15 Issues Prioritaires (Détaillées)

Les 15 issues ci‑dessous sont prêtes à être créées sur GitHub.

---
 
### 1. [A1] Endpoint de configuration `/api/v1/config`

**Contexte**: Le frontend a besoin de connaître les feature flags et infos build sans rebuild.
**Objectif**: Exposer un endpoint léger JSON: `{ feature_flags:{...}, build:{hash,timestamp}, version }`.
**Tâches**:

- [ ] Créer route DRF GET `/api/v1/config/`
- [ ] Lire flags depuis modèle (ou settings si absent) + fallback par défaut
- [ ] Inclure un hash de commit (env GIT_SHA) si disponible
- [ ] Ajouter cache headers (ETag ou max-age faible 60s)
- [ ] Test API (statut 200 + structure)
**Critères d'acceptation**:
- [ ] Appel renvoie 200 <50ms p95 (local)
- [ ] Clés absentes → valeurs par défaut
- [ ] Pas d'info sensible exposée
**Tests**: APITestCase structure; test absence de flags.
**Risques**: Minimiser fuite d'env. Mitigation: whitelist champs.
**Labels**: backend,infra,feature-flags,priority:high,size:S
**Dépendances**: Aucune

---
 
### 2. [A3] Système de Feature Flags backend

**Contexte**: Les features Match / Social / Versus doivent être activables progressivement.
**Objectif**: Modèle `FeatureFlag(name, enabled, rollout_percentage)` + service cache.
**Tâches**:

- [ ] Modèle + migration
- [ ] Admin Django list + search
- [ ] Service `flags.is_enabled("social_profile")`
- [ ] Cache local (invalidation post-save signal)
- [ ] Intégrer dans endpoint config (A1)
- [ ] Tests unitaires service
**Critères**:
- [ ] Désactiver flag coupe code path (ex: /social endpoints 404 ou 403)
- [ ] Lecture O(1) (pas de requête par appel)
**Tests**: création, toggle, cache invalidation.
**Risques**: Oubli gating; ajouter check liste PR.
**Labels**: backend,feature-flags,priority:high,size:M
**Dépendances**: A1

---
 
### 3. [C1] Endpoint profil social (GET `/social/profile/me`)

**Contexte**: Front affiche actuellement stub.
**Objectif**: Retourner profil + stats calculées.
**Tâches**:

- [ ] Serializer profil (gamertag, display_name, bio, avatar_url, is_public)
- [ ] Stats (total_matches, successful_matches, friends_count, pending_requests)
- [ ] Vue DRF avec permission IsAuthenticated
- [ ] Test API (profil existant / création auto)
**Critères**:
- [ ] Création automatique profil si manquant
- [ ] Temps <80ms (local) p95
**Labels**: backend,social,priority:high,size:S
**Dépendances**: A1, A3

---
 
### 4. [C3] Hook frontend `useSocialProfile` réel

**Contexte**: Hook stub renvoie toujours null.
**Objectif**: Intégrer endpoint C1 avec cache local & refresh.
**Tâches**:

- [ ] Implémenter fetch + setState loading/error/data
- [ ] Bouton reload (optionnel) / invalidation
- [ ] Gestion 401 → redirection login
- [ ] Tests manuels (affichage profil)
**Critères**:
- [ ] Profil s'affiche sans erreur
- [ ] Fallback spinner & message d'erreur
**Labels**: frontend,social,priority:high,size:S
**Dépendances**: C1

---
 
### 5. [B1] Implémentation RecommendationService (phase 1)

**Contexte**: Code actuel mélange simulation & placeholders.
**Objectif**: Retourner au moins 10 items hétérogènes avec filtrage contenu déjà vu.
**Tâches**:

- [ ] Implémenter stratégies: films (TMDB), séries (TMDB), livres (Google Books ou fallback), musique (mock)
- [ ] Factoriser `_filter_user_content`
- [ ] Ajout TTL cache API externe (APICache)
- [ ] Log timing par catégorie
- [ ] Test unitaire par méthode (retourne liste non vide ou [])
**Critères**:
- [ ] Aucune duplication d'external_id dans réponse
- [ ] Scoring compatibilité ≥ présent (placeholder accepté)
**Labels**: backend,reco,priority:high,size:M
**Dépendances**: A3

---
 
### 6. [B2] Endpoint action match (POST `/match/action/`)

**Contexte**: Front a besoin de persister like/dislike/add.
**Objectif**: Créer/mettre à jour UserPreference + maj stats profil.
**Tâches**:

- [ ] Serializer entrée (external_id, source, content_type, action, title, metadata)
- [ ] Upsert UserPreference
- [ ] Incrément stats (total_matches, successful si added)
- [ ] Réponse `{success, preference_id, action}`
- [ ] Test API (idempotence même action)
**Critères**:
- [ ] Conflits gérés sans 500
- [ ] Action hors enum → 400
**Labels**: backend,match,priority:high,size:S
**Dépendances**: B1

---
 
### 7. [B5] Remplacer stub `useMatchRecommendations`

**Contexte**: Hook actuel renvoie listes vides.
**Objectif**: Connecter endpoints B1/B2 + navigation items.
**Tâches**:

- [ ] Implémenter fetch initial + pagination naïve (refetch quand proche fin)
- [ ] Méthode `submitAction(reco, action)` → POST B2 puis retire item
- [ ] Gestion erreurs (retry bouton)
- [ ] Petits tests unitaires (mocks) ou storybook interactif (optionnel)
**Critères**:
- [ ] Like/Dislike/Add retirent l'item de l'UI
- [ ] Aucun crash si réponse lente
**Labels**: frontend,match,priority:high,size:M
**Dépendances**: B1, B2

---
 
### 8. [D1] Endpoint ajout ami (POST `/social/friends/add`)

**Contexte**: Ajout impossible actuellement.
**Objectif**: Créer enregistrement Friendship status=pending (ou accepted si self? refusé).
**Tâches**:

- [ ] Validation gamertag existant
- [ ] Empêcher doublon (unique requester/addressee peu importe ordre)
- [ ] Rate limit basique (throttle class DRF)
- [ ] Réponse `{success, friendship_id, status}`
- [ ] Test API (doublon -> 400)
**Critères**:
- [ ] Pas d'auto‑ajout soi‑même
**Labels**: backend,social,priority:high,size:M
**Dépendances**: C1

---
 
### 9. [D2] Endpoint liste amis (GET `/social/friends/`)

**Contexte**: Interface a besoin d'une liste des ACCEPTED.
**Objectif**: Retourner tableau friends minimal.
**Tâches**:

- [ ] Query friendships où user impliqué & status=accepted
- [ ] Mapper FriendUser (côté autre)
- [ ] Test API (cas 0 amis)
**Critères**:
- [ ] Performant <50ms local (utiliser select_related)
**Labels**: backend,social,size:S,priority:high
**Dépendances**: D1

---
 
### 10. [D4] Implémenter UI liste & ajout amis (FriendsManager)

**Contexte**: Composant partiellement stub.
**Objectif**: Brancher sur D1 + D2 + feedback utilisateur.
**Tâches**:

- [ ] Hook `useFriends` réel (friends + refresh)
- [ ] Hook `useFriendSearch` → POST add + retour état
- [ ] Affichage pending count (si future D5) placeholder
- [ ] Toast succès / erreur
**Critères**:
- [ ] Ajout ami valide → apparaît après refresh auto
**Labels**: frontend,social,size:M,priority:high
**Dépendances**: D2

---
 
### 11. [E2] Création match Versus (POST `/versus/matches`)

**Contexte**: Service côté modèle présent mais pas exposé.
**Objectif**: Créer FriendMatch + sessions (rounds) initiales.
**Tâches**:

- [ ] Serializer (target_gamertag, rounds default=10)
- [ ] Validation: sont amis (Friendship ACCEPTED)
- [ ] Génération contenu (RecommendationService catégorisé)
- [ ] Réponse minimal `{match_id, total_rounds}`
- [ ] Test API (non amis -> 400)
**Critères**:
- [ ] Création unique si aucun match actif identique (optionnel warning)
**Labels**: backend,versus,size:M,priority:high
**Dépendances**: D2, B1

---
 
### 12. [E4] Soumettre choix Versus (POST `/versus/matches/{id}/choice`)

**Contexte**: Progression match dépend des choix.
**Objectif**: Enregistrer choix utilisateur pour round courant + avancer si complété.
**Tâches**:

- [ ] Validation tour / utilisateur
- [ ] Détection match (liked/liked)
- [ ] Mise à jour score + passage round suivant
- [ ] Réponse avec état session/match
**Critères**:
- [ ] Double soumission même round -> 400
**Labels**: backend,versus,size:M,priority:high
**Dépendances**: E2

---
 
### 13. [E6] Interface VersusMatch (remplacer stub)

**Contexte**: UI actuelle montre un placeholder.
**Objectif**: Afficher progression (round X/Y, scores, contenu) + boutons Like/Dislike/Skip.
**Tâches**:

- [ ] Hook `useVersusSession` (GET current-session)
- [ ] Action submitChoice (E4)
- [ ] Affichage animation match réussi
- [ ] Fin de match: résumé + CTA rejouer
**Critères**:
- [ ] Aucune action possible quand session complétée
**Labels**: frontend,versus,size:L,priority:high
**Dépendances**: E4

---
 
### 14. [F1] Logging structuré (backend)

**Contexte**: Besoin de corrélation & debug production.
**Objectif**: Format JSON log + request id + niveau.
**Tâches**:

- [ ] Config logging dict (formatter JSON)
- [ ] Middleware request id (UUID header X-Request-ID)
- [ ] Log entrée/sortie key fields (path, status, duration ms)
- [ ] Logger service reco timings
- [ ] Tests unitaires middleware (inject id)
**Critères**:
- [ ] Aucune fuite token dans logs
**Labels**: backend,observability,size:M,priority:high
**Dépendances**: A1

---
 
### 15. [G1] Rate limiting global & endpoints sensibles

**Contexte**: Protéger contre abus simples avant bêta.
**Objectif**: DRF throttling (par IP + par utilisateur) sur endpoints clés.
**Tâches**:

- [ ] Config DEFAULT_THROTTLE_RATES (auth, match action, add friend)
- [ ] Classe throttle custom si besoin (clé user-id or IP fallback)
- [ ] Tests: dépassement → 429
- [ ] Doc README section Sécurité rapide
**Critères**:
- [ ] Match action limitée mais UX fluide (ex: 60/min)
**Labels**: backend,security,size:S,priority:high
**Dépendances**: A1

## Gabarit Issue Standard

```md
### Contexte
...
### Objectif
...
### Tâches
- [ ] ...
### Critères d’acceptation
- [ ] ...
### Tests
Unit: ... / API: ... / Front: ...
### Risques / Mitigation
...
Labels: ...,size:?,priority:?
Dépendances: #ID
```

## Suivi

Créer un Projet GitHub (Backlog / In Progress / Review / Done) et lier les issues ci‑dessus.

---
_Dernière mise à jour : initial commit roadmap._
