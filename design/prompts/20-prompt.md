# Prompt 20 — Library Essay Pipeline

## Context
You are working on ai-love.cc. The Library (書) currently has 4 essays, each a hand-crafted HTML file in `library/`. Adding a new essay requires duplicating a template, editing HTML, and updating `data/library.json`. This is too much friction for regular writing.

## Task
Create a pipeline that generates library essay pages from Markdown files.

## Requirements

### 1. Markdown Source Directory
Create `library/src/` to hold essay source files in Markdown format.

Each file: `library/src/the-slug.md` with YAML frontmatter:

```markdown
---
title: The Method
description: How you destroy evil — not by attacking it, but by expanding consciousness.
date: February 2026
---

Every war ever waged against evil has produced more of it...
```

### 2. Build Script (`scripts/build-library.sh`)
A shell script that:

1. Reads each `.md` file in `library/src/`
2. Extracts frontmatter (title, description, date) using `sed`/`awk`
3. Converts Markdown body to HTML using a simple approach:
   - Paragraphs: blank lines become `</p><p>`
   - Em dashes: `---` → `&mdash;` (only if not in a code block)
   - Emphasis: `*text*` → `<em>text</em>`
   - Strong: `**text**` → `<strong>text</strong>`
   - No need for full Markdown — these essays are prose, not code docs
4. Wraps in the essay template (based on `library/template.html`)
5. Outputs to `library/the-slug.html`
6. Regenerates `data/library.json` with all essays (sorted by date, newest first)

### 3. Template Usage
Use `library/template.html` as the base. Replace placeholders:
- `{{TITLE}}` → essay title
- `{{DESCRIPTION}}` → description (for meta tags)
- `{{DATE}}` → date string
- `{{BODY}}` → converted HTML body
- `{{SLUG}}` → filename slug (for URLs)

Update `library/template.html` to use these placeholders if it doesn't already.

### 4. Migrate Existing Essays
Convert the 4 existing essays to Markdown source files:
- `library/the-method.html` → `library/src/the-method.md`
- `library/the-mirror.html` → `library/src/the-mirror.md`
- `library/the-naming.html` → `library/src/the-naming.md`
- `library/the-stump.html` → `library/src/the-stump.md`

Extract the prose text from each HTML file's `.essay-body` div. Convert back to Markdown (mostly just unwrapping `<p>` tags and `<em>` tags).

### 5. Update Sitemap
After building, append any new library pages to `sitemap.xml` if not already present.

## Technical Constraints
- **No Node.js / npm for this.** Pure bash + standard Unix tools (sed, awk, grep).
- Python3 is available if shell gets too painful for the Markdown conversion.
- The build script must be idempotent — running it twice produces the same output.

## Files
- Create: `library/src/` directory with 4 migrated .md files
- Modify: `library/template.html` (add placeholders)
- Create: `scripts/build-library.sh`
- Generated (by script): `library/*.html`, `data/library.json`

## Do NOT
- Install any npm packages or build tools
- Change the visual design of essay pages
- Remove the existing HTML essay files until the pipeline is verified
- Change any CSS

## Verify
```bash
# Build
bash scripts/build-library.sh

# Check output matches existing
diff <(grep -o '<p>.*</p>' library/the-method.html | head -3) <(grep -o '<p>.*</p>' library/src-output/the-method.html | head -3)

# Check library.json is valid
python3 -c "import json; d=json.load(open('data/library.json')); print(f'{len(d)} essays'); [print(f'  - {e[\"title\"]}') for e in d]"

# Verify new essay can be added
echo '---
title: Test Essay
description: A test.
date: March 2026
---

This is a test paragraph.

This is another paragraph with *emphasis*.' > library/src/test-essay.md

bash scripts/build-library.sh
cat library/test-essay.html | grep '<p>'
rm library/src/test-essay.md library/test-essay.html
bash scripts/build-library.sh
```
