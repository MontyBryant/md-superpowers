---
name: pdf-convert
description: >
  DEPRECATED in v0.3 — use the `convert` skill instead. Convert PDF
  documents to clean, searchable markdown using Docling with automated
  post-processing. Use when the user asks to "convert pdf", "pdf to
  markdown", "process pdf", "convert this document", "docling", "pdf
  conversion", "add reference pdf", "extract text from pdf", or provides
  a PDF they want turned into markdown. Note: this skill is for PDF-to-
  markdown conversion, not for creating, merging, or filling PDFs.
---

> ⚠️ **Deprecated in v0.3 — use the `convert` skill instead.**
>
> `pdf-convert` was a docling-first PDF-to-markdown converter that assumed
> docling would always be available and fell over when it wasn't (notably
> in the Cowork sandbox where docling OOMs on any real PDF due to RAM
> constraints). The newer `convert` skill handles any document type (PDF,
> docx, pptx, epub, html, image), adaptively picks the right engine for
> the environment, and includes the full enrichment pipeline that
> `pdf-convert` was missing — diagrams → mermaid, comparisons → tables,
> structured frontmatter, per-recipe success criteria, and more.
>
> **Migration:** anywhere you would have invoked `pdf-convert`, invoke
> `convert` instead. Same entry point, better output, broader input
> support. See `skills/convert/SKILL.md` for the full design.
>
> This skill is kept on disk for one release cycle so existing muscle
> memory still works. It will be removed in v0.4. The `pdf_postprocess.py`
> and `pdf_verify.py` helper scripts remain available and are referenced
> by the new skill's knowledge bank.

# PDF-to-Markdown Conversion (legacy)

Convert PDF documents to clean, searchable markdown using Docling (IBM-backed, MIT license), automated post-processing, and LLM quality review.

## Setup (lazy — only on first use)

Docling is a heavier dependency (~30-60s install). Install it only when this skill is first invoked in a session — not on startup. Run silently:

```bash
pip install docling --break-system-packages 2>&1 | tail -3
```

Verify with `docling --version`. If it fails, retry without suppressing output to diagnose.

The skill also bundles two Python scripts:
- `${CLAUDE_PLUGIN_ROOT}/skills/pdf-convert/scripts/pdf_postprocess.py`
- `${CLAUDE_PLUGIN_ROOT}/skills/pdf-convert/scripts/pdf_verify.py`

## Workflow

Six steps, always in this order.

### Step 1 — Convert

```bash
docling "input.pdf" --to md --image-export-mode referenced --output "output_dir/"
```

**Always** use `--image-export-mode referenced`. The default `embedded` mode encodes images as base64 inline, bloating files 5-10x and wasting tokens in search indexes.

If the user specifies an output directory, use it. Otherwise, place output alongside the source PDF or in a sensible `md/` subdirectory.

### Step 2 — Post-process

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/pdf-convert/scripts/pdf_postprocess.py" "output_dir/converted-file.md"
```

Handles: image path cleanup, HTML entity decoding, Unicode ligature fixes, heading hierarchy repair, false heading demotion, duplicate line removal, glyph ID stripping, watermark removal, and excess blank line cleanup. See `references/knowledge-bank.md` for the full catalogue of known issues.

### Step 3 — Auto-verify

```bash
python "${CLAUDE_PLUGIN_ROOT}/skills/pdf-convert/scripts/pdf_verify.py" "output_dir/converted-file.md" --reference-dir "source_dir/"
```

Fast mechanical check (<1 second). Catches: glyph ID remnants, broken image refs, base64 embedding, flat heading hierarchy, orphaned list items. Also flags when `--force-ocr` may be needed.

### Step 4 — LLM Review (you do this)

The real quality gate. Read three sections of the converted file:

1. **First ~80 lines** — Clear title? Coherent intro? Or fragments and image refs?
2. **Middle section (~40% through)** — Body text flowing? Paragraphs complete? Headings logical?
3. **Last ~60 lines** — Proper ending (conclusion, references)? Or trailing artifacts?
4. **Any area flagged by Step 3**

Assess for: readability, heading structure, table quality, content completeness, formatting, image references.

### Step 5 — Fix

Decision tree:
- Content looks good → proceed to Step 6
- Minor formatting issues → fix in-place (edit the markdown directly)
- Major content loss (glyph artifacts, missing body text, fragments only) → re-convert with `--force-ocr`, re-run Steps 2-4
- New document-specific issue → note it for future knowledge bank updates

### Step 6 — Index (if applicable)

If QMD or another search index is available:

```bash
qmd update && qmd embed
```

If no search index is configured, skip this step.

## When to use `--force-ocr`

Only when standard extraction fails — producing glyph IDs (`/gidXXXXX`), empty body text, or skeleton output. Most PDFs extract fine in standard mode. Force-OCR is 2-3x slower but reads rendered page images via OCR, bypassing font encoding issues entirely.

```bash
docling "input.pdf" --to md --image-export-mode referenced --force-ocr --output "output_dir/"
```

## Batch conversion

For multiple PDFs in the same directory:

```bash
SCRIPTS="${CLAUDE_PLUGIN_ROOT}/skills/pdf-convert/scripts"

for pdf in source_dir/*.pdf; do
  docling "$pdf" --to md --image-export-mode referenced --output "output_dir/"
done

for md in output_dir/*.md; do
  python "$SCRIPTS/pdf_postprocess.py" "$md"
done

for md in output_dir/*.md; do
  python "$SCRIPTS/pdf_verify.py" "$md" --reference-dir "source_dir/"
done
```

Then do the LLM review (Step 4) for each file. For large batches, prioritise the longest files and any the verifier flagged.

## Where to save converted files

| Context | Destination |
|---|---|
| Research reference for a domain | `research/<domain>/references/md/` |
| Bridging Worlds reference | `projects/bridging-worlds/references/md/` |
| General reading material | `readings/<category>/` |
| Quick capture, unsure | `ops/inbox/` |

All paths relative to the user's workspace root.

## Quality expectations by document type

| Type | Expected quality | Notes |
|------|-----------------|-------|
| Clean reports/essays | Excellent | Minimal post-processing needed |
| Books | Good | TOC may be messy, body text clean |
| Books with custom fonts | Good (with --force-ocr) | Standard extraction may fail entirely |
| Institutional reports | Good | Complex layouts handled well |
| Academic papers (two-column) | Fair | Post-processor fixes most issues, some residual noise |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `docling: command not found` | Not installed this session | Re-run setup step |
| Glyph IDs (`/gidXXXXX`) in output | Font encoding issue | Re-convert with `--force-ocr` |
| Huge file size | Base64 embedded images | Check `--image-export-mode referenced` was used |
| Empty or near-empty output | Scanned/image-only PDF | Use `--force-ocr` |
| Broken image references | Image export path mismatch | Check output dir structure, run post-processor |

## References

For the full catalogue of known conversion issues and lessons learned, read `${CLAUDE_PLUGIN_ROOT}/skills/pdf-convert/references/knowledge-bank.md`.
