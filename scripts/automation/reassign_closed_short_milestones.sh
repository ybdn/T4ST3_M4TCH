#!/usr/bin/env bash
set -eo pipefail
# Ré-assigne les issues encore liées aux milestones courtes fermées (M1..M6)
# vers les milestones descriptives correspondantes.
# Usage: ./scripts/automation/reassign_closed_short_milestones.sh [--dry-run] [--verbose]

dry_run=false
verbose=false
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) dry_run=true; shift;;
    --verbose) verbose=true; shift;;
    *) echo "Arg inconnu: $1"; exit 1;;
  esac
done

command -v gh >/dev/null || { echo "gh CLI manquant"; exit 2; }

map_target() {
  case "$1" in
    M1) echo "M1 - Core Match Alpha";;
    M2) echo "M2 - Social v1";;
    M3) echo "M3 - Versus v1";;
    M4) echo "M4 - Qualité/Obs";;
    M5) echo "M5 - Bêta Fermée";;
    M6) echo "M6 - Bêta Elargie";;
    *) return 1;;
  esac
}

# Récupère tous milestones (ouverts + fermés)
ms_json=$(gh api repos/:owner/:repo/milestones?state=all)

# Identifie les milestones courtes fermées
for code in M1 M2 M3 M4 M5 M6; do
  short_num=$(echo "$ms_json" | jq ".[] | select(.title == \"$code\") | .number")
  short_state=$(echo "$ms_json" | jq -r ".[] | select(.title == \"$code\") | .state")
  [[ -z "$short_num" || "$short_num" == "null" ]] && continue
  target_name=$(map_target "$code" || true)
  [[ -z "$target_name" ]] && continue
  target_num=$(echo "$ms_json" | jq ".[] | select(.title == \"$target_name\") | .number")
  if [[ -z "$target_num" || "$target_num" == "null" ]]; then
    echo "Milestone descriptive manquante pour $code ($target_name)" >&2
    continue
  fi
  $verbose && echo "Analyse $code (short=$short_num state=$short_state -> target=$target_name #$target_num)"
  # Récupère issues encore sur le milestone court (utilise API directe par numéro)
  issues=$(gh api repos/:owner/:repo/issues --paginate -F milestone="$short_num" -F state=all --jq '.[].number' || true)
  if [[ -z "$issues" ]]; then
    $verbose && echo "  Aucune issue à déplacer"
    continue
  fi
  while read -r issue; do
    [[ -z "$issue" ]] && continue
    if $dry_run; then
      echo "[DRY-RUN] Reassign issue #$issue -> $target_name"
    else
      gh issue edit "$issue" --milestone "$target_name" >/dev/null && echo "Issue #$issue -> $target_name"
    fi
  done <<< "$issues"

done

echo "Terminé (dry_run=$dry_run)"
