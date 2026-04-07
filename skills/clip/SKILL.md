---
name: clip
description: >
  Clip web pages to clean markdown using Defuddle. Use when the user asks to
  "clip this", "save this page", "defuddle", "web clip", "save this url",
  "clip to markdown", "save as markdown", "grab this article", "clip article",
  "save this link", "convert page to markdown", or provides a URL they want
  saved as markdown. Also trigger when the user pastes a URL and asks to
  "read", "save", or "capture" it.
---

# Clip — Web Page to Markdown

Clip any web page to a clean markdown file using Defuddle. Strips navigation, ads, and chrome — keeps the article content with structured YAML frontmatter.

## Setup

Defuddle must be installed before first use each session. Run this silently before the first clip — don't ask the user, just do it:

```bash
export PATH="${CLAUDE_PLUGIN_ROOT}/../../../.local/node_modules/.bin:/sessions/cool-exciting-euler/.local/bin:$PATH"
npm install -g defuddle --prefix /sessions/cool-exciting-euler/.local 2>/dev/null
```

Verify with `defuddle --version` (expect 0.15.0+). If it fails, try the install again without `2>/dev/null` to see errors.

## How to Clip

The plugin bundles a Node.js script at `${CLAUDE_PLUGIN_ROOT}/skills/clip/scripts/md_defuddle.js`.

Always ensure PATH includes defuddle before running:

```bash
export PATH="/sessions/cool-exciting-euler/.local/bin:$PATH"
node "${CLAUDE_PLUGIN_ROOT}/skills/clip/scripts/md_defuddle.js" <url> [output_path]
```

Without an output path, the script prints to stdout (useful for previewing). With a path, it writes the file and confirms.

## Output Format

Each clipped file gets YAML frontmatter followed by the article body:

```yaml
---
title: "Article Title"
source: https://example.com/article
domain: example.com
author: "Author Name"
site: "Site Name"
description: "Page meta description"
published: 2026-01-15
clipped: 2026-04-07
language: en
word_count: 1240
image: https://example.com/og-image.jpg
---

# Article Title

[clean article content...]
```

Fields are omitted when not present in page metadata. `clipped` is always today's date.

## Where to Save

If the user specifies a destination, use it. Otherwise, choose based on context:

| Context | Destination |
|---|---|
| General article or long read | `readings/web/YYYY-MM-DD_Title.md` |
| Research reference for a specific domain | `research/<domain>/references/YYYY-MM-DD_Title.md` |
| Bridging Worlds project reference | `projects/bridging-worlds/references/md/YYYY-MM-DD_Title.md` |
| Quick capture, unsure where it belongs | `ops/inbox/YYYY-MM-DD_Title.md` |

All paths are relative to the user's workspace root.

## Deriving Filenames

When the user doesn't specify a filename:

1. Prefix with today's date: `YYYY-MM-DD_`
2. Title-case the article title, replace spaces with hyphens, strip special characters
3. Truncate to ~60 characters
4. Append `.md`

Example: "How Regen Network's ecocredits work" becomes `2026-04-07_How-Regen-Networks-Ecocredits-Work.md`

## After Clipping

1. Tell the user where the file was saved and show the frontmatter summary (title, author, word count)
2. If saved to `ops/inbox/`, note it's queued for processing
3. If saved to `readings/` or `research/`, mention that `qmd update && qmd embed` can index it for search (if QMD is available)

## Handling Failures

| Symptom | Likely cause | Fix |
|---|---|---|
| `defuddle: command not found` | Not installed this session | Re-run the setup step |
| Empty or very short content | JS-rendered page (SPA) | Tell the user — Defuddle only parses static HTML |
| Garbled title or author | Bad page metadata | Clip anyway, suggest editing the frontmatter |
| Timeout after 30s | Slow or unresponsive server | Retry once, then report failure |
| Network error | Sandbox network restrictions | Check if the domain is reachable with `curl -I <url>` |
