#!/usr/bin/env bash
set -euo pipefail
# Consolidation des milestones courtes (M1..M6) vers les milestones descriptives déjà existantes.
# Mapping:
#   M1  -> M1 - Core Match Alpha
#   M2  -> M2 - Social v1
#   M3  -> M3 - Versus v1
#   M4  -> M4 - Qualité/Obs
#   M5  -> M5 - Bêta Fermée
#   M6  -> M6 - Bêta Elargie
# M0 reste intact (Baseline Stable)
# Usage: ./scripts/automation/consolidate_milestones.sh [--dry-run]

dry_run=false
if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=true
fi

command -v gh >/dev/null || { echo "gh CLI manquant"; exit 2; }


short_numbers=$(gh api repos/:owner/:repo/milestones --jq '.[] | select(.title|IN("M1","M2","M3","M4","M5","M6")) | .number')
if [[ -z "$short_numbers" ]]; then
  echo "Aucun milestone court trouvé. Rien à faire."; exit 0
fi

declare -A target_names=(
  [M1]="M1 - Core Match Alpha"
  [M2]="M2 - Social v1"
  [M3]="M3 - Versus v1"
  [M4]="M4 - Qualité/Obs"
  [M5]="M5 - Bêta Fermée"
  [M6]="M6 - Bêta Elargie"
)

changed=0

for code in M1 M2 M3 M4 M5 M6; do
  short_ms_num=$(gh api repos/:owner/:repo/milestones --jq ".[] | select(.title == \"$code\") | .number" || true)
  [[ -z "$short_ms_num" ]] && continue
  target_name="${target_names[$code]}"
  # Vérifie existence du milestone cible
  target_ms_num=$(gh api repos/:owner/:repo/milestones --jq ".[] | select(.title == \"$target_name\") | .number" || true)
  if [[ -z "$target_ms_num" ]]; then
    echo "Milestone cible manquant: $target_name (créer d'abord)" >&2
    continue
  fi
  echo "Traitement $code (#$short_ms_num) -> $target_name (#$target_ms_num)"
  # Lister issues du milestone court
  issues=$(gh issue list --milestone "$code" --state all --json number --jq '.[].number' || true)
  if [[ -z "$issues" ]]; then
    echo "  (aucune issue)"
  else
    while read -r num; do
      [[ -z "$num" ]] && continue
      if $dry_run; then
        echo "  [DRY-RUN] Reassign issue #$num vers $target_name"
      else
        gh issue edit "$num" --milestone "$target_name" >/dev/null
        echo "  Issue #$num réassignée"
        changed=$((changed+1))
      fi
    done <<< "$issues"
  fi
  # Fermer milestone court s'il est vide après migration
  if ! $dry_run; then
    remaining=$(gh issue list --milestone "$code" --state all --json number --jq 'length')
    if [[ "$remaining" -eq 0 ]]; then
      gh api repos/:owner/:repo/milestones/$short_ms_num -X PATCH -f state=closed >/dev/null
      echo "  Milestone court $code fermé"
    else
      echo "  Milestone $code non vide (restants=$remaining)"
    fi
  else
    echo "  [DRY-RUN] Fermer $code si vide"
  fi

done

echo "Fini. Issues réassignées: $changed (dry_run=$dry_run)"
