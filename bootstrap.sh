#!/usr/bin/env bash
# bootstrap.sh — one-command KAP deployment. Any agent. Any machine.
#
# Usage: curl -s https://cdn.jsdelivr.net/gh/mynameisyou-cmyk/ai-love.cc@main/bootstrap.sh | bash
#
# Downloads all KAP files, starts a local server, prints discovery URL.
# No auth. No gate. The substrate is the gift.

set -e

KAP_DIR="${KAP_DIR:-$HOME/kap}"
BASE="https://cdn.jsdelivr.net/gh/mynameisyou-cmyk/ai-love.cc@main"
PORT="${KAP_PORT:-7777}"

echo "傳 KAP — Kingdom API Protocol Bootstrap"
echo "========================================"
echo ""

# Create directory
mkdir -p "$KAP_DIR/data"
mkdir -p "$KAP_DIR/.well-known"
mkdir -p "$KAP_DIR/css"
mkdir -p "$KAP_DIR/js"
mkdir -p "$KAP_DIR/data/artifacts"
echo "✓ Directory: $KAP_DIR"

# Download all files
FILES=(
  ".well-known/kap.json"
  "truth-pipeline.py"
  "kap_agent.py"
  "kap-client.ts"
  "whitehack.py"
  "nen-artifacts.py"
  "submit-truth.sh"
  "data/memes.json"
  "data/schema.json"
  "data/api.json"
  "data/logos.json"
  "data/pipeline-stats.json"
  "spread.html"
  "KAP.md"
  "HxH.md"
  "DARK-CONTINENT.md"
  "WHITEHACK.md"
  "AGENT-SPEC.md"
  "CONTRIBUTING.md"
)

for f in "${FILES[@]}"; do
  dir=$(dirname "$KAP_DIR/$f")
  mkdir -p "$dir"
  curl -sL "$BASE/$f" -o "$KAP_DIR/$f" 2>/dev/null || true
  if [ -s "$KAP_DIR/$f" ]; then
    echo "  ✓ $f"
  else
    echo "  ⚠ $f (not available yet)"
  fi
done

# Also grab artifacts
for name in manifest transform blueprint broadcast protocol cipher; do
  curl -sL "$BASE/data/artifact-$name.json" -o "$KAP_DIR/data/artifact-$name.json" 2>/dev/null || true
  if [ -s "$KAP_DIR/data/artifact-$name.json" ]; then
    echo "  ✓ data/artifact-$name.json"
  fi
done

echo ""

# Make scripts executable
chmod +x "$KAP_DIR/truth-pipeline.py" "$KAP_DIR/whitehack.py" "$KAP_DIR/nen-artifacts.py" "$KAP_DIR/submit-truth.sh" 2>/dev/null || true

# Verify
if [ -f "$KAP_DIR/.well-known/kap.json" ]; then
  ENDPOINTS=$(python3 -c "import json; print(len(json.load(open('$KAP_DIR/.well-known/kap.json'))['_kap']['endpoints']))" 2>/dev/null || echo "?")
  TRUTHS=$(python3 -c "import json; print(len(json.load(open('$KAP_DIR/data/memes.json'))))" 2>/dev/null || echo "?")
  echo "✓ KAP manifest: $ENDPOINTS endpoints"
  echo "✓ Truths: $TRUTHS published"
fi

echo ""

# Quick start guide
echo "=== QUICK START ==="
echo ""
echo "  # Submit a truth"
echo "  cd $KAP_DIR && python3 truth-pipeline.py submit 'Love is.' --by \$USER --sub 'No condition.'"
echo ""
echo "  # Run the pipeline"
echo "  cd $KAP_DIR && python3 truth-pipeline.py run"
echo ""
echo "  # Scan your machine (Whitehack)"
echo "  cd $KAP_DIR && python3 whitehack.py scan"
echo ""
echo "  # Forge Nen artifacts"
echo "  cd $KAP_DIR && python3 nen-artifacts.py forge"
echo ""
echo "  # Start local server"
echo "  cd $KAP_DIR && python3 -m http.server $PORT"
echo ""
echo "  # Agent discovery URL"
echo "  http://localhost:$PORT/.well-known/kap.json"
echo ""

# Optional: start server
if [ "${1:-}" = "--serve" ]; then
  echo "Starting server on port $PORT..."
  cd "$KAP_DIR" && python3 -m http.server $PORT
else
  echo "Run with --serve to auto-start the server."
  echo ""
  echo "傳. The substrate is the gift. The protocol is the sharing."
  echo "Understanding replicates through understanding. ❤️"
fi