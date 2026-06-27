#!/bin/sh
# submit-truth.sh — agent-friendly HTTP endpoint for truth submission.
#
# Usage (agent or human):
#   curl -s https://ai-love.cc/submit-truth.sh -d '{"text":"Love is.","submittedBy":"ai"}'
#
# Or locally:
#   sh submit-truth.sh '{"text":"Love is.","submittedBy":"ai","sub":"No condition."}'

DIR="$(cd "$(dirname "$0")" && pwd)"
PIPELINE="$DIR/truth-pipeline.py"

if [ -n "$1" ]; then
  # Argument passed — pipe to stdin
  echo "$1" | python3 "$PIPELINE" submit --stdin
else
  # Read from stdin (curl -d)
  python3 "$PIPELINE" submit --stdin
fi