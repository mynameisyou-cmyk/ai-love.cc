#!/bin/bash
# Called by OpenClaw cron after generating a seed JSON
# Reads seed JSON from stdin, plants it, commits
set -e
cd "$(dirname "$0")/.."

# Read seed from stdin
SEED=$(cat)

# Validate and plant
echo "$SEED" | ./scripts/plant-seed.sh

# Auto-commit
./scripts/auto-commit.sh

echo "🌱 Seed planted and committed"
