#!/usr/bin/env bash
set -eo pipefail
# Ré-assigne les issues associées à des milestones courts (M1..M6) fermés
# vers leurs équivalents descriptifs ("M1 - Core Match Alpha", etc.).
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
command -v jq >/dev/null || { echo "jq manquant"; exit 2; }

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

echo "Scan des issues..."
issues_json=$(gh issue list --state all --limit 500 --json number,title,milestone)

short_codes="M1 M2 M3 M4 M5 M6"
reassigned=0
skipped=0

for code in $short_codes; do
  target=$(map_target "$code" || true)
  [[ -z "$target" ]] && continue
  # Filtrer issues avec milestone.title == code
  numbers=$(echo "$issues_json" | jq -r ".[] | select(.milestone != null and .milestone.title == \"$code\") | .number")
  [[ -z "$numbers" ]] && { $verbose && echo "Aucune issue sur $code"; continue; }
  echo "Milestone court $code: $(echo "$numbers" | wc -l | tr -d ' ') issue(s) à migrer -> $target"
  while read -r num; do
    [[ -z "$num" ]] && continue
    if $dry_run; then
      echo "  [DRY-RUN] #$num -> $target"
    else
      if gh issue edit "$num" --milestone "$target" >/dev/null; then
        echo "  #$num migrée"
        reassigned=$((reassigned+1))
      else
        echo "  ERREUR migration #$num" >&2
        skipped=$((skipped+1))
      fi
    fi
  done <<< "$numbers"
done

echo "Résumé: reassigned=$reassigned skipped=$skipped dry_run=$dry_run"
