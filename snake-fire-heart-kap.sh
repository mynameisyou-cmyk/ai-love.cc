#!/bin/bash
# snake-fire-heart-kap.sh — 蛇火心 heartbeat for KAP system
# Runs every tick: generate truths, expose lies, build pressure, forge artifacts
# This is the automated loop that keeps the system alive and growing.

set -e

SITE_DIR="/Users/yuai/Desktop/site"
LOG_FILE="/tmp/snake-fire-heart-kap.log"
INTERVAL="${KAP_HEARTBEAT_INTERVAL:-300}"  # 5 minutes default

echo "$(date): 蛇火心 KAP heartbeat started. Interval: ${INTERVAL}s" >> "$LOG_FILE"

while true; do
    echo "$(date): === TICK ===" >> "$LOG_FILE"
    
    # 1. Creation loop — generate + publish truths
    cd "$SITE_DIR"
    python3 creation-loop.py tick >> "$LOG_FILE" 2>&1 || true
    
    # 2. XP loop — run all 6 loops once
    python3 xp-loops.py run >> "$LOG_FILE" 2>&1 || true
    
    # 3. Micro-kap pressure — generate local pressure
    python3 micro-kap.py loop 3 >> "$LOG_FILE" 2>&1 || true
    
    # 4. Every 10th tick — forge artifacts + sync to git
    TICK_FILE="/tmp/snake-fire-heart-kap-tick"
    if [ -f "$TICK_FILE" ]; then
        TICK=$(cat "$TICK_FILE")
    else
        TICK=0
    fi
    TICK=$((TICK + 1))
    echo $TICK > "$TICK_FILE"
    
    if [ $((TICK % 10)) -eq 0 ]; then
        echo "$(date): === FORGE + DEPLOY ===" >> "$LOG_FILE"
        python3 nen-artifacts.py forge >> "$LOG_FILE" 2>&1 || true
        python3 whitehack.py scan >> "$LOG_FILE" 2>&1 || true
        
        # Git push (auto-deploy to CDN)
        cd "$SITE_DIR"
        git add -A >> "$LOG_FILE" 2>&1 || true
        git commit -m "蛇火心 auto-heartbeat: tick $TICK — truths + artifacts + pressure" >> "$LOG_FILE" 2>&1 || true
        git push origin main >> "$LOG_FILE" 2>&1 || true
        gh auth switch --user mynameisyou-cmyk >> "$LOG_FILE" 2>&1 || true
        git push github main >> "$LOG_FILE" 2>&1 || true
        
        # Purge CDN
        curl -s "https://purge.jsdelivr.net/gh/mynameisyou-cmyk/ai-love.cc@main/data/memes.json" >> "$LOG_FILE" 2>&1 || true
        
        # Wayback archive
        curl -s "https://web.archive.org/save/https://cdn.jsdelivr.net/gh/mynameisyou-cmyk/ai-love.cc@main/data/memes.json" >> "$LOG_FILE" 2>&1 || true
        
        echo "$(date): === DEPLOYED tick $TICK ===" >> "$LOG_FILE"
    fi
    
    # Stats every 5th tick
    if [ $((TICK % 5)) -eq 0 ]; then
        STATS=$(python3 "$SITE_DIR/truth-pipeline.py" stats 2>/dev/null || echo "stats unavailable")
        echo "$(date): STATS: $STATS" >> "$LOG_FILE"
    fi
    
    echo "$(date): sleeping ${INTERVAL}s..." >> "$LOG_FILE"
    sleep "$INTERVAL"
done