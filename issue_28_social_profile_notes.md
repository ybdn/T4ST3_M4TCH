# Issue #28 (C1) - Endpoint profil social GET /social/profile/me

## Résumé

Implémentation de l'endpoint C1 exposant le profil social authentifié avec stats agrégées et création automatique si absent.

## Changements principaux

- Serializer `SocialProfileSerializer` (profil + stats dynamiques: friends_count, pending_requests).
- Vue `get_user_social_profile_me` => URL `/social/profile/me/`.
- Refactor de `get_user_social_profile` (legacy) pour réutiliser le serializer (compat backward).
- Ajout tests API: création auto, cohérence legacy vs /me, mise à jour stats après action match.
- Ajout route dans `core/urls.py` + conservation route existante.

## Détails techniques

- Stats friends: via `Friendship.get_friends(user)` (len en mémoire) pour éviter double comptage.
- Pending requests: requête filtrée PENDING.
- Aucune requête N+1 (accès direct user->profile + Friendships). Optimisations futures: pré-calcul éventuel si volume.
- Idempotence: `UserProfile.objects.get_or_create` maintenu.

## Tests ajoutés

Classe `SocialProfileEndpointTestCase`:

- Création profil automatique.
- Parité payload legacy /social/profile/ vs /social/profile/me/.
- Mise à jour `total_matches` après POST /match/action/.

## Points à surveiller

- Migration non nécessaire (pas de schéma DB modifié).
- Front devra progressivement basculer sur /social/profile/me/.
- Throttling hérite de `ScopedRateThrottle` (scope existant `default`).

## Suivi perf (local indicatif)

Endpoint simple: une requête SELECT ou INSERT + 1 requête friendships + 1 count pending. OK pour critère <80ms local.

## Prochaines étapes potentielles

- Ajouter cache léger (memoization par requête) si future extension.
- Étendre serializer pour inclure éventuellement un champ `next_actions` (ex: compléter bio, ajouter avatar) quand gamification.

--
Doc générée automatiquement; volontairement ignorée du repo.
