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
