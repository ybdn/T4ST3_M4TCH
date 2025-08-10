# Issue #27 – Rate Limiting Global & Endpoints Sensibles

Implémentation d’un mécanisme de throttling (rate limiting) via Django REST Framework.

## Objectifs

1. Protéger les endpoints sensibles (auth, register, recherches, actions match, appels externes) contre l’abus.
2. Fournir des valeurs par défaut raisonnables + possibilité de surcharger via variables d’environnement.
3. Permettre la désactivation complète via `RATE_LIMIT_ENABLED=false` (utile pour perf tests / seed).
4. Avoir un relâchement automatique en environnement DEBUG (multiplicateur 50x).

## Modifications Principales

### settings.py

- Ajout des classes de throttling DRF: `ScopedRateThrottle`, `UserRateThrottle`, `AnonRateThrottle`.
- Ajout de `RATE_LIMIT_ENABLED` et d’un bloc conditionnel pour construire `DEFAULT_THROTTLE_RATES`.
- Scopes définis: `auth`, `auth_refresh`, `register`, `search`, `match_action`, `external`.

### views.py

- Ajout décorateur `@throttle_classes([ScopedRateThrottle])` sur endpoints sensibles + santé.
- Les scopes effectifs associés seront déterminés côté router / view attr si besoin d’un raffinement futur.
  (Actuellement DRF associera le nom de la vue fonction à un scope implicite; possibilité d’étendre.)

## Variables d’Environnement (optionnelles)

```env
THROTTLE_ANON=200/day
THROTTLE_USER=2000/day
THROTTLE_AUTH=30/minute
THROTTLE_AUTH_REFRESH=120/hour
THROTTLE_REGISTER=20/hour
THROTTLE_SEARCH=240/minute
THROTTLE_MATCH_ACTION=600/minute
THROTTLE_EXTERNAL=120/minute
RATE_LIMIT_ENABLED=True
```

En DEBUG les valeurs par défaut sont multipliées par 50.

## Points de Suivi Ultérieur

- Ajouter tests unitaires dédiés (429) pour un ou deux endpoints critiques.
- Exposer les limites courantes dans l’endpoint de config si besoin frontend.
- Introduire un backend Redis pour un comptage distribué en production (actuellement en mémoire / cache défaut).

## Risques & Mitigations

- Faux positifs sur burst court: valeurs relativement permissives initialement.
- Environnement local: multiplicateur évite de gêner le dev.

## Done

Issue #27 couverte avec configuration flexible.
