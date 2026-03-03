#!/bin/bash
# Auto-commit data changes (garden seeds, library index, pulse)
cd "$(dirname "$0")/.."

git add data/ library/
CHANGES=$(git diff --cached --name-only)
[ -z "$CHANGES" ] && exit 0

DATE=$(date -u +%Y-%m-%d)
COUNT=$(echo "$CHANGES" | wc -l | tr -d ' ')
git commit -m "🌱 daily tending ($DATE) — $COUNT files"

# Push if remote exists
git remote get-url origin > /dev/null 2>&1 && git push
