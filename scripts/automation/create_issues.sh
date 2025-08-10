#!/usr/bin/env bash
set -euo pipefail

# Requires: gh CLI authenticated (gh auth login) and repo set (cwd = repo root)
# Usage: ./scripts/automation/create_issues.sh [--dry-run] [--verbose] [--limit N] [--resume CODE]

dry_run=false
verbose=false
limit=0
resume=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) dry_run=true; shift;;
    --verbose) verbose=true; shift;;
    --limit) limit=${2:-0}; shift 2;;
    --resume) resume=${2:-""}; shift 2;;
    *) echo "Arg inconnu: $1"; exit 1;;
  esac
done

command -v gh >/dev/null || { echo "gh CLI manquant"; exit 2; }
command -v jq >/dev/null || { echo "jq manquant"; exit 2; }

if ! gh auth status >/dev/null 2>&1; then
  echo "Authentification gh invalide"; exit 3; fi

total=$(jq 'length' scripts/automation/issues.json)
echo "Lecture issues.json ($total items)"

count=0
processed=0
skipped=0

start_time=$(date +%s)

jq -c '.[]' scripts/automation/issues.json | while read -r issue; do
  code=$(echo "$issue" | jq -r '.code')
  if [[ -n "$resume" && "$code" != "$resume" && $processed -eq 0 ]]; then
    # Skip until resume code hit
    continue
  fi
  processed=$((processed+1))
  title=$(echo "$issue" | jq -r '.title')
  body=$(echo "$issue" | jq -r '.body')
  milestone=$(echo "$issue" | jq -r '.milestone')
  labels=$(echo "$issue" | jq -r '.labels | join(",")')

  [[ $limit -gt 0 && $count -ge $limit ]] && { echo "Limite atteinte ($limit)."; break; }

  $verbose && echo "----\nTraitement $code ($title)"

  # Milestone
  ms_number=$(gh api repos/:owner/:repo/milestones --jq ".[] | select(.title == \"$milestone\") | .number" || true)
  if [[ -z "$ms_number" ]]; then
    if $dry_run; then
      echo "[DRY-RUN] create milestone $milestone"
      ms_number=0
    else
      gh api repos/:owner/:repo/milestones -f title="$milestone" >/dev/null || { echo "ERREUR création milestone $milestone"; exit 10; }
      ms_number=$(gh api repos/:owner/:repo/milestones --jq ".[] | select(.title == \"$milestone\") | .number")
      echo "Milestone créée: $milestone (#$ms_number)"
    fi
  fi

  # Existence
  if gh issue list --state all --search "$title" --json title --limit 100 --jq ".[] | select(.title == \"$title\") | .title" | grep -q .; then
    echo "Skip existant: $title"
    skipped=$((skipped+1))
    continue
  fi

  if $dry_run; then
    echo "[DRY-RUN] create issue: $title (labels=$labels milestone=$milestone)"
  else
    if gh issue create --title "$title" --body "$body" --label "$labels" --milestone "$milestone" >/dev/null; then
      echo "Issue créée: $code"
      count=$((count+1))
    else
      echo "ERREUR création issue: $code" >&2
      exit 20
    fi
  fi

  # Petit sleep pour éviter rate-limit spam (optionnel)
  $dry_run || sleep 0.5
done

end_time=$(date +%s)
echo "---\nRésumé: créées=$count skipped=$skipped temps=$((end_time-start_time))s dry_run=$dry_run"
