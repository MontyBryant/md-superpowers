# Changelog — mdpowers-cowork

A narrative record of how this plugin evolves. Updated after significant work sessions, not per-commit. Focuses on the "why" and "what changed" rather than granular diffs.

---

## 2026-04-09 — v0.3: the `convert` skill and the agentic scaffold

Major release. Two big changes landed together.

**The `convert` skill replaces `pdf-convert`.** A real-world test converting the Kwaxala Overview 2026 pitch deck exposed several fundamental problems with the old `pdf-convert` skill. First, it was docling-first and docling OOMs in the Cowork sandbox (3.8GB RAM), so the skill couldn't actually run on its target environment. Second, it only handled PDFs — users wanted consistent treatment for docx, pptx, and other formats. Third, it produced flat text extraction with no semantic enrichment, meaning the output was technically markdown but not meaningfully navigable or AI-readable. A 25-slide pitch deck full of flowcharts and layered stack diagrams came out as 25 pages of loose captions with no structure.

The redesign started with a superpowers-style brainstorming session that went through six chunks of design decisions with explicit approval gates. The chosen architecture is an adaptive orchestrator: five phases (Probe → Plan → Execute → Enrich → Verify), seven recipe archetypes, six enrichment playbooks, and a three-tier planning budget (tight / standard / deep) that scales ceremony to document complexity. Simple one-pagers get tight treatment with no ceremony; novel or complex documents get a plan artifact and user review before execution. The key design principle — "guides not rails" — was named explicitly after the user pointed out that over-prescription can itself be a failure mode.

The new skill delegates to built-in Anthropic skills (`pdf`, `docx`, `pptx`, `xlsx`) as first-choice engines wherever possible, with ordered fallback to docling, marker, pymupdf, and pandoc. Graceful degradation is the default: when a preferred engine isn't available, the skill drops silently to the next one and records `quality: degraded` in the output frontmatter so downstream work can find and re-convert those files later.

Seven recipes: `slide-deck-visual`, `academic-paper`, `institutional-report`, `book-longform`, `scanned-document`, `simple-onepager`, `hybrid-novel`. Each declares its own triggers, engine preferences, enrichment playbook IDs, output shape, and success criteria. The `hybrid-novel` catch-all always escalates to deep planning, which means genuinely unfamiliar source types get a proper plan written before execution instead of a best-guess attempt.

Six playbooks in `skills/convert/references/enrichment/`: P1 diagrams-to-structured (the Kwaxala lesson — image + description + mermaid), P2 comparisons-to-tables, P3 images-and-assets, P4 semantic-descriptions, P5 frontmatter-and-metadata, P6 cross-references-and-glossary. Each is a short document (50–230 lines) with a worked example, deviation guidance, and explicit failure modes. P1 and P5 are the load-bearing ones and are written in full detail.

`pdf-convert` is deprecated in place with a notice at the top of its SKILL.md pointing users at `convert`. It stays on disk for one release cycle (removed in v0.4) to preserve existing muscle memory. The helper scripts (`pdf_postprocess.py`, `pdf_verify.py`) remain available and will be merged into `convert/references/` when `pdf-convert` is removed.

**Adopted the agentic scaffold.** Simultaneously added the top-level scaffold files matching the `agentic-scaffold-plugin` architecture: CLAUDE.md (agent instructions, conventions, boundaries), DECISIONS.md (ADR-style decision log with four initial entries documenting this session's choices), ROADMAP.md (near-term / future / parking-lot / decided), and this CHANGELOG.md. README.md was updated to match the new structure and reflect the new skill.

The scaffold adoption was motivated by the plugin's growth from a single-purpose PDF converter into a broader ingestion toolkit. Without explicit conventions, future skill authoring would drift inconsistently. The scaffold gives future contributors (human or agent) a clear map of how the plugin is organised and documents the design principles that should inform new skills.

Four decisions are logged in DECISIONS.md for this release: D001 (agentic scaffold adoption), D002 (convert replaces pdf-convert), D003 ("guides not rails" as project-wide principle), D004 (built-in Anthropic skills preferred as first-choice engines).

Design spec and staging README for this release are preserved in `bridging-worlds/labs/mdpowers-v2-convert/` for historical reference.

**Next:** validate the new skill against 3-5 real documents of different archetypes, tune recipes based on observed gaps, then publish the v0.3 release tag. See ROADMAP.md for details.

---

## 2025-11-ish — v0.2: clip + pdf-convert

Initial public release. Two skills: `/clip` for web-page-to-markdown via Defuddle, and `/pdf-convert` for PDF-to-markdown via Docling with automated post-processing. Both use lazy dependency installation (~2s for defuddle, ~30-60s for docling) so nothing installs at plugin load time.

`/clip` produces markdown with YAML frontmatter (title, source, author, date, word count). `/pdf-convert` produces markdown with referenced images, automated post-processing for common extraction artifacts (ligatures, glyph IDs, heading detection), and an LLM-based quality review pass.

Tested extensively in Claude Code on macOS with a reference corpus of 16 PDFs. Known issues catalogued in `skills/pdf-convert/references/knowledge-bank.md`.

<!-- Scaffold sources: keep-a-changelog (adapted to narrative style), bridging-worlds narrative changelog pattern, agentic-scaffold-plugin v0.1.0 -->
