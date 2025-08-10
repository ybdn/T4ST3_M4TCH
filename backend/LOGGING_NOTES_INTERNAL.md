# Document interne: Mise en place du logging structuré (Issue #26)

## Objectif

Fournir un logging structuré JSON pour faciliter l'observabilité (agrégation dans Loki / ELK / etc.), ajout de request_id et correlation_id.

## Résumé des changements

1. Ajout dépendance python-json-logger dans requirements.txt.
2. Ajout config LOGGING dans tastematch_api/settings.py avec:
   - Format JSON ou console via LOG_FORMAT
   - Filtres: RequestIdFilter, SamplingFilter
   - Middleware RequestIdMiddleware pour injection request_id / correlation_id
3. Ajout de variables env: LOG_LEVEL, LOG_FORMAT, LOG_SAMPLING_RATE
4. Ajout de champs standard: asctime, levelname, name, message, request_id, correlation_id, host, environment

## Utilisation

Par défaut: LOG_FORMAT=json et LOG_LEVEL=INFO.
Pour du debug verbeux local: LOG_LEVEL=DEBUG LOG_FORMAT=console.

Headers supportés entrant:

- X-Request-ID (sinon généré en UUID v4)
- X-Correlation-ID (optionnel, sinon fallback sur request_id)

Headers sortant:

- X-Request-ID reflète la valeur utilisée.

## Échantillonnage

LOG_SAMPLING_RATE permet de réduire le volume de logs DEBUG en production (0 < rate <= 1). Ne filtre pas les niveaux >= INFO.

## Améliorations futures possibles

1. Ajout d'enrichissement utilisateur (user_id) via un autre middleware ou un logging filter custom.
2. Export OpenTelemetry: instrumenter Django + Requests.
3. Ajout d'un handler vers stdout + un handler vers un fichier rotatif (si besoin d'archive locale).
4. Ajout d'un trace_id si OpenTelemetry actif.

## Tests manuels rapides

Lancement serveur dev puis curl:
`curl -H "X-Request-ID: test-123" http://localhost:8000/api/v1/config/`
Vérifier présence du champ request_id et format JSON.

Fin.
