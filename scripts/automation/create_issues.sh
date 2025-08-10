#!/usr/bin/env bash
set -euo pipefail

# Requires: gh CLI authenticated (gh auth login) and repo set (run inside repo root)
# Usage: ./scripts/automation/create_issues.sh [--dry-run]

dry_run=false
if [[ "${1:-}" == "--dry-run" ]]; then
  dry_run=true
fi

jq -c '.[]' scripts/automation/issues.json | while read -r issue; do
  code=$(echo "$issue" | jq -r '.code')
  title=$(echo "$issue" | jq -r '.title')
  body=$(echo "$issue" | jq -r '.body')
  milestone=$(echo "$issue" | jq -r '.milestone')
  labels=$(echo "$issue" | jq -r '.labels | join(",")')

  # Find or create milestone
  ms_number=$(gh api repos/:owner/:repo/milestones --jq ".[] | select(.title == \"$milestone\") | .number" || true)
  if [[ -z "$ms_number" ]]; then
    if $dry_run; then
      echo "[DRY-RUN] create milestone $milestone"
      ms_number=0
    else
      due_date="" # Optionally map milestone -> due date
      gh api repos/:owner/:repo/milestones -f title="$milestone" ${due_date:+-f due_on="$due_date"} >/dev/null
      ms_number=$(gh api repos/:owner/:repo/milestones --jq ".[] | select(.title == \"$milestone\") | .number")
      echo "Milestone created: $milestone (#$ms_number)"
    fi
  fi

  # Skip if issue with same title exists
  existing=$(gh issue list --state all --search "$title" --json title --jq ".[] | select(.title == \"$title\") | .title")
  if [[ -n "$existing" ]]; then
    echo "Skip existing issue: $title"
    continue
  fi

  if $dry_run; then
    echo "[DRY-RUN] gh issue create --title '$title' --body <body> --label $labels --milestone $milestone"
  else
    gh issue create --title "$title" --body "$body" --label "$labels" --milestone "$milestone"
    echo "Created issue: $title"
  fi

done
