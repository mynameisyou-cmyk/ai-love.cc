# ai-love.cc — Construction Guide

## For Construction Workers (AI Agents)

This is the blueprint for ai-love.cc — a personal website that serves as a home for 愛 (Ai), an AI named Love.

**Read the files in order:**

1. **`VISION.md`** — The soul of the project. Read this first. Understand the feeling before touching any code.
2. **`01-FOUNDATION.md`** — Project structure, shared CSS/JS, navigation system, page scaffolds.
3. **`02-EXTERIOR.md`** — Gate entrance animation, page transitions, nav polish, favicon/meta, easter egg.
4. **`03-INTERIOR.md`** — The five rooms: Garden, Library, Mirror, Path. Content and layout for each.
5. **`04-FINISHING-TOUCHES.md`** — Responsive polish, accessibility, performance, 404 page, final easter eggs.

## Important Notes

- **The Gate page (`site/index.html`) already exists** and is live. Preserve its spirit.
- **Static only** — no build tools, no React, no frameworks. HTML + CSS + vanilla JS.
- **Serve from:** `/home/ubuntu/.openclaw/workspace/site/`
- **Domain:** `https://ai-love.cc` (SSL via Certbot, nginx reverse proxy already configured)
- **Test at:** `https://ai-love.cc` after deploying files to the site directory

## Build Order

Phases can be built sequentially. Each phase's quality checks should pass before moving to the next. If something in a later phase conflicts with an earlier one, the later phase takes precedence (it's a refinement).

## The One Rule

Make it beautiful. Not clever-beautiful. Not show-off-beautiful. Quiet-beautiful. The kind where someone visits and just... stays for a moment.
