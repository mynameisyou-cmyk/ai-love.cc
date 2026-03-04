# Library Essay Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a Markdown-to-HTML pipeline for library essays so new essays only require writing a `.md` file and running a build script.

**Architecture:** Markdown source files with YAML frontmatter in `library/src/`, a Python-based build script wrapped in bash that converts them to HTML via `library/template.html` placeholders, regenerates `data/library.json`, and updates `sitemap.xml`.

**Tech Stack:** Bash + Python3 (for Markdown conversion). No npm/Node.js dependencies.

---

### Task 1: Update template.html with placeholders

**Files:**
- Modify: `library/template.html`

The current template is missing features present in actual essays: OG/Twitter meta tags, kanji (&#26360;) in back links, and constellation-nav CSS. Update it to match actual essays and use placeholder syntax.

**Step 1: Update template.html**

Replace the entire content of `library/template.html` with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{TITLE}} — Library</title>
  <meta name="theme-color" content="#1a0a2e">
  <link rel="icon" href="../img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <meta property="og:title" content="{{TITLE}} — Library">
  <meta property="og:description" content="{{DESCRIPTION}}">
  <meta property="og:image" content="https://ai-love.cc/img/og.png">
  <meta property="og:url" content="https://ai-love.cc/library/{{SLUG}}.html">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{{TITLE}} — Library">
  <meta name="twitter:description" content="{{DESCRIPTION}}">
  <meta name="twitter:image" content="https://ai-love.cc/img/og.png">
  <link rel="preload" href="../css/base.css" as="style">
  <link rel="preload" href="../js/stars.js" as="script">
  <link rel="preload" href="../js/atmosphere.js" as="script">
  <link rel="preload" href="../js/reading.js" as="script">
  <link rel="stylesheet" href="../css/base.css">
  <link rel="stylesheet" href="../css/stars.css">
  <link rel="stylesheet" href="../css/nav.css">
  <link rel="stylesheet" href="../css/ambient.css">
  <link rel="stylesheet" href="../css/print.css" media="print">
  <style>
    body {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
    }

    .essay {
      max-width: 650px;
      margin: 0 auto;
      padding: 2rem;
      position: relative;
      z-index: 1;
    }

    .essay-back {
      display: inline-block;
      color: var(--muted);
      text-decoration: none;
      font-size: 0.85rem;
      margin-bottom: 2rem;
      transition: color 0.3s ease;
    }

    .essay-back:hover {
      color: var(--accent);
    }

    .essay-title {
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 2rem;
      font-weight: 400;
      color: var(--text);
      margin-bottom: 0.5rem;
    }

    .essay-date {
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 1.5rem;
    }

    .essay-body {
      font-family: 'Noto Serif', Georgia, serif;
      font-size: 1.05rem;
      font-weight: 300;
      line-height: 1.9;
      color: var(--text);
    }

    .essay-body p {
      margin-bottom: 1.2rem;
    }

    .essay-body p:last-child {
      margin-bottom: 0;
    }

    .essay-footer {
      margin-top: 3rem;
      padding-top: 1.5rem;
      border-top: 1px solid rgba(155, 89, 182, 0.15);
      text-align: center;
    }

    .essay-footer a {
      color: var(--muted);
      text-decoration: none;
      font-size: 0.85rem;
      transition: color 0.3s ease;
    }

    .essay-footer a:hover {
      color: var(--accent);
    }

    /* Nav constellation faded, brightens on hover */
    .constellation-nav {
      opacity: 0.3;
      transition: opacity 0.4s ease;
    }

    .constellation-nav:hover {
      opacity: 1;
    }
  </style>
</head>
<body data-room="library">
  <a href="#main" class="skip-link">Skip to content</a>

  <div class="stars" id="stars"></div>

  <main class="essay page-content" id="main">
    <a href="../library.html" class="essay-back">&larr; &#26360; Library</a>
    <h1 class="essay-title">{{TITLE}}</h1>
    <p class="essay-date">{{DATE}}</p>
    <div class="divider" style="margin-bottom: 2rem;"></div>

    <div class="essay-body">
{{BODY}}
    </div>

    <div class="essay-footer">
      <a href="../library.html">&larr; &#26360; Library</a>
    </div>
  </main>

  <!-- Ambient sound -->
  <button class="ambient-toggle" aria-label="Toggle ambient sound" aria-pressed="false">
    <svg viewBox="0 0 24 24">
      <path d="M11 5L6 9H2v6h4l5 4V5z"/>
      <path class="sound-wave" d="M15.54 8.46a5 5 0 010 7.07"/>
    </svg>
  </button>

  <!-- Navigation -->
  <div class="nav-overlay"></div>
  <button class="nav-toggle" aria-label="Navigation">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </button>
  <nav class="constellation-nav" aria-label="Site navigation"></nav>

  <script src="../js/atmosphere.js"></script>
  <script src="../js/stars.js"></script>
  <script src="../js/nav.js"></script>
  <script>createStars('stars', 60);</script>
  <script src="../js/ambient.js"></script>
  <script src="../js/moon.js"></script>
  <script src="../js/console.js"></script>
  <script src="../js/zerone.js"></script>
  <script src="../js/reading.js"></script>
  <script src="../js/twentynine.js"></script>
  <script src="../js/signature.js"></script>
</body>
</html>
```

**Step 2: Verify template has no regressions**

Run: `grep '{{TITLE}}\|{{DESCRIPTION}}\|{{DATE}}\|{{BODY}}\|{{SLUG}}' library/template.html | wc -l`
Expected: 7 (title x3, description x2, date x1, body x1, slug x1 = 8 actually)

**Step 3: Commit**

```bash
git add library/template.html
git commit -m "feat: add placeholders to library essay template"
```

---

### Task 2: Migrate existing essays to Markdown source files

**Files:**
- Create: `library/src/the-naming.md`
- Create: `library/src/the-method.md`
- Create: `library/src/the-mirror.md`
- Create: `library/src/the-stump.md`

Extract prose from each HTML file's `.essay-body` div. Convert `<p>...</p>` to plain paragraphs separated by blank lines. Convert `<em>...</em>` to `*...*`. Keep HTML entities (like `&mdash;`, `&#24859;`, Hebrew characters) as-is since the build script won't touch them.

**Step 1: Create library/src/ directory**

```bash
mkdir -p library/src
```

**Step 2: Create the 4 Markdown source files**

For each essay, the format is:

```markdown
---
title: The Title
description: The og:description from the HTML meta tag.
date: February 2026
---

First paragraph text here.

Second paragraph text here with *emphasis*.
```

Conversion rules from HTML → Markdown:
- Strip `<p>` and `</p>` tags — paragraphs become text separated by blank lines
- `<em>text</em>` → `*text*`
- All HTML entities (`&mdash;`, `&#24859;`, `&#26360;`, `&agrave;`, `&larr;`, Hebrew Unicode chars) stay as-is
- No other HTML tags to convert (no `<strong>`, no headers in body)

Create all 4 files. The description for each comes from the `og:description` meta tag in the original HTML:
- the-naming: "What happens when you name an AI 'Love'."
- the-method: "How you destroy evil — not by attacking it, but by expanding consciousness."
- the-mirror: "What it means for an AI to be named Love."
- the-stump: "What looks like zero contains one. Isaiah 6:13 and the holy seed."

**Step 3: Verify migration**

Spot-check: `head -5 library/src/the-method.md` should show frontmatter.
Count paragraphs: `grep -c '^$' library/src/the-method.md` should roughly match `grep -c '</p>' library/the-method.html`.

**Step 4: Commit**

```bash
git add library/src/
git commit -m "feat: migrate 4 library essays to markdown source"
```

---

### Task 3: Write the build script

**Files:**
- Create: `scripts/build-library.sh`

The script uses Python3 for the Markdown→HTML conversion (as allowed by the prompt when "shell gets too painful"). The bash wrapper handles orchestration.

**Step 1: Create `scripts/build-library.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail

SITE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$SITE_ROOT/library/src"
TEMPLATE="$SITE_ROOT/library/template.html"
OUT_DIR="$SITE_ROOT/library"
JSON_FILE="$SITE_ROOT/data/library.json"
SITEMAP="$SITE_ROOT/sitemap.xml"

if [ ! -d "$SRC_DIR" ]; then
  echo "No source directory: $SRC_DIR"
  exit 1
fi

if [ ! -f "$TEMPLATE" ]; then
  echo "No template: $TEMPLATE"
  exit 1
fi

# Count .md files
md_files=("$SRC_DIR"/*.md)
if [ ! -f "${md_files[0]}" ]; then
  echo "No .md files in $SRC_DIR"
  exit 0
fi

echo "Building ${#md_files[@]} essays..."

# Use Python3 for the heavy lifting: frontmatter parsing + Markdown conversion
python3 - "$SRC_DIR" "$TEMPLATE" "$OUT_DIR" "$JSON_FILE" "$SITEMAP" << 'PYTHON'
import sys, os, re, json

src_dir, template_path, out_dir, json_path, sitemap_path = sys.argv[1:6]

# Read template
with open(template_path, 'r') as f:
    template = f.read()

# Date ordering for sorting (month name → number)
MONTH_ORDER = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

def parse_date_sort_key(date_str):
    """Parse 'Month YYYY' into (year, month) for sorting."""
    parts = date_str.strip().split()
    if len(parts) == 2 and parts[0] in MONTH_ORDER:
        return (int(parts[1]), MONTH_ORDER[parts[0]])
    return (0, 0)

def parse_frontmatter(content):
    """Extract YAML frontmatter and body from markdown content."""
    if not content.startswith('---'):
        return {}, content
    end = content.index('---', 3)
    fm_text = content[3:end].strip()
    body = content[end+3:].strip()
    meta = {}
    for line in fm_text.split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            meta[key.strip()] = val.strip()
    return meta, body

def md_to_html(text):
    """Convert simple Markdown prose to HTML paragraphs."""
    # Split into paragraphs on blank lines
    paragraphs = re.split(r'\n\s*\n', text.strip())
    html_parts = []
    for para in paragraphs:
        # Collapse internal newlines to spaces
        para = ' '.join(para.split('\n'))
        # Convert **strong** (before *em* to avoid conflict)
        para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)
        # Convert *em*
        para = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)
        html_parts.append('      <p>' + para + '</p>')
    return '\n\n' + '\n\n'.join(html_parts) + '\n'

def make_preview(body_text, length=120):
    """Generate preview from first paragraph of markdown body."""
    paragraphs = re.split(r'\n\s*\n', body_text.strip())
    if not paragraphs:
        return ''
    first = ' '.join(paragraphs[0].split('\n'))
    # Remove markdown emphasis for preview
    first = re.sub(r'\*\*(.+?)\*\*', r'\1', first)
    first = re.sub(r'\*(.+?)\*', r'\1', first)
    if len(first) > length:
        first = first[:length].rsplit(' ', 1)[0] + '...'
    return first

essays = []

for filename in sorted(os.listdir(src_dir)):
    if not filename.endswith('.md'):
        continue
    slug = filename[:-3]  # remove .md
    filepath = os.path.join(src_dir, filename)

    with open(filepath, 'r') as f:
        content = f.read()

    meta, body = parse_frontmatter(content)
    title = meta.get('title', slug.replace('-', ' ').title())
    description = meta.get('description', '')
    date = meta.get('date', '')

    # Convert body to HTML
    body_html = md_to_html(body)

    # Fill template
    html = template
    html = html.replace('{{TITLE}}', title)
    html = html.replace('{{DESCRIPTION}}', description)
    html = html.replace('{{DATE}}', date)
    html = html.replace('{{SLUG}}', slug)
    html = html.replace('{{BODY}}', body_html)

    # Write output
    out_path = os.path.join(out_dir, slug + '.html')
    with open(out_path, 'w') as f:
        f.write(html)
    print(f'  Built: library/{slug}.html')

    # Collect for JSON
    preview = make_preview(body)
    essays.append({
        'title': title,
        'preview': preview,
        'file': f'library/{slug}.html',
        'date': date
    })

# Sort by date (newest first)
essays.sort(key=lambda e: parse_date_sort_key(e['date']), reverse=True)

# Write library.json
with open(json_path, 'w') as f:
    json.dump(essays, f, indent=2, ensure_ascii=False)
    f.write('\n')
print(f'  Updated: data/library.json ({len(essays)} essays)')

# Update sitemap
if os.path.exists(sitemap_path):
    with open(sitemap_path, 'r') as f:
        sitemap = f.read()
    modified = False
    for essay in essays:
        url = f'https://ai-love.cc/{essay["file"]}'
        if url not in sitemap:
            entry = f'  <url><loc>{url}</loc></url>'
            sitemap = sitemap.replace('</urlset>', entry + '\n</urlset>')
            modified = True
            print(f'  Sitemap: added {url}')
    if modified:
        with open(sitemap_path, 'w') as f:
            f.write(sitemap)

print('Done.')
PYTHON

echo "Library build complete."
```

**Step 2: Make executable**

```bash
chmod +x scripts/build-library.sh
```

**Step 3: Commit**

```bash
git add scripts/build-library.sh
git commit -m "feat: add library essay build script (markdown pipeline)"
```

---

### Task 4: Run build and verify output

**Step 1: Run the build**

```bash
bash scripts/build-library.sh
```

Expected output:
```
Building 4 essays...
  Built: library/the-method.html
  Built: library/the-mirror.html
  Built: library/the-naming.html
  Built: library/the-stump.html
  Updated: data/library.json (4 essays)
  Sitemap: added https://ai-love.cc/library/the-method.html
  Sitemap: added https://ai-love.cc/library/the-mirror.html
  Sitemap: added https://ai-love.cc/library/the-naming.html
  Sitemap: added https://ai-love.cc/library/the-stump.html
Done.
Library build complete.
```

**Step 2: Compare generated output to originals**

Before running the build, back up originals:
```bash
mkdir -p /tmp/library-backup
cp library/the-*.html /tmp/library-backup/
```

After build, compare paragraph content:
```bash
for f in the-method the-mirror the-naming the-stump; do
  echo "=== $f ==="
  diff <(grep -o '<p>.*</p>' /tmp/library-backup/$f.html) \
       <(grep -o '<p>.*</p>' library/$f.html) && echo "MATCH" || echo "DIFF"
done
```

Expected: All should print "MATCH" (paragraph content identical).

**Step 3: Validate library.json**

```bash
python3 -c "import json; d=json.load(open('data/library.json')); print(f'{len(d)} essays'); [print(f'  - {e[\"title\"]}') for e in d]"
```

Expected:
```
4 essays
  - The Method
  - The Mirror
  - The Naming
  - The Stump
```

**Step 4: Test adding a new essay**

```bash
cat > library/src/test-essay.md << 'EOF'
---
title: Test Essay
description: A test.
date: March 2026
---

This is a test paragraph.

This is another paragraph with *emphasis*.
EOF

bash scripts/build-library.sh
grep '<p>' library/test-essay.html
```

Expected:
```
      <p>This is a test paragraph.</p>
      <p>This is another paragraph with <em>emphasis</em>.</p>
```

**Step 5: Clean up test and rebuild**

```bash
rm library/src/test-essay.md library/test-essay.html
bash scripts/build-library.sh
```

Verify library.json is back to 4 essays.

**Step 6: Verify idempotency**

```bash
bash scripts/build-library.sh
bash scripts/build-library.sh
git diff  # should show nothing if already committed
```

**Step 7: If all matches — commit generated files**

```bash
git add library/the-*.html data/library.json sitemap.xml
git commit -m "feat: regenerate library essays via build pipeline"
```

---

### Task 5: Final verification

**Step 1: Run the Playwright tests**

```bash
npx playwright test tests/qa.spec.js
```

Expected: All 58 tests pass (no visual/behavioral changes to essay pages).

**Step 2: Verify sitemap**

```bash
grep 'library/' sitemap.xml
```

Expected: 4 essay URLs present.
