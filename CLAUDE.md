# CLAUDE.md — mdpowers-cowork

Markdown superpowers for knowledge gardens. A Claude Cowork plugin providing adaptive document-to-markdown conversion and web clipping, optimised for AI-readable output.

## Project Identity

- **Name:** mdpowers-cowork
- **Stack:** Claude Agent SDK plugin (skills + helper scripts in Python and JavaScript)
- **Purpose:** Turn documents (PDF, docx, pptx, epub, html, images) and web pages into clean, structured, AI-readable markdown
- **Repository:** https://github.com/montymerlin/mdpowers-cowork
- **Authored by:** Monty Merlin

## Directory Structure

```
mdpowers-plugin/
├── CLAUDE.md                       # this file — agent instruction set
├── README.md                       # human-facing overview
├── DECISIONS.md                    # architectural decision log
├── ROADMAP.md                      # future directions
├── CHANGELOG.md                    # narrative change history
├── .claude-plugin/
│   └── plugin.json                 # plugin manifest
├── .claude/
│   └── settings.local.json         # Claude Code settings
└── skills/
    ├── convert/                    # v0.3 — adaptive document-to-markdown
    │   ├── SKILL.md
    │   └── references/
    │       ├── recipes.md
    │       ├── matching.md
    │       ├── environments.md
    │       ├── anti-patterns.md
    │       ├── roadmap.md
    │       └── enrichment/
    │           ├── P1-diagrams-to-structured.md
    │           ├── P2-comparisons-to-tables.md
    │           ├── P3-images-and-assets.md
    │           ├── P4-semantic-descriptions.md
    │           ├── P5-frontmatter-and-metadata.md
    │           └── P6-cross-references-and-glossary.md
    ├── clip/                       # web-page-to-markdown via Defuddle
    │   ├── SKILL.md
    │   └── scripts/md_defuddle.js
    └── pdf-convert/                # DEPRECATED in v0.3, removed in v0.4
        ├── SKILL.md                # deprecation notice + legacy docs
        ├── references/knowledge-bank.md
        └── scripts/
            ├── pdf_postprocess.py
            └── pdf_verify.py
```

## Key Conventions

### Skill authoring

- Each skill lives in `skills/<skill-name>/` with a `SKILL.md` at the root
- Long reference material (recipes, playbooks, catalogues) goes in `skills/<skill-name>/references/` and is loaded on demand
- Helper scripts (Python, JavaScript) go in `skills/<skill-name>/scripts/` and are invoked via `${CLAUDE_PLUGIN_ROOT}/skills/<skill-name>/scripts/...`
- Frontmatter descriptions must include the full trigger phrase vocabulary users are likely to say — ambiguity in triggering is the most common cause of skills not being invoked
- Every skill should articulate its own deviation guidance — "guides not rails" is the project-wide principle

### Naming

- **Files:** kebab-case for markdown documents, snake_case for Python scripts, camelCase or kebab-case for JavaScript
- **Skills:** short, generic, memorable names (`convert`, not `adaptive-document-converter`)
- **Playbooks:** numbered `P1-*.md`, `P2-*.md`, etc. for easy cross-reference from recipes
- **Branches:** `feature/<short>`, `fix/<short>`, version branches like `v0.3-convert-skill`

### Commits

- Concise message focusing on "why" not "what"
- Reference decisions by number when relevant (e.g., "per Decision 003")
- Never auto-commit — always show the diff first and wait for user approval

### Documentation

- **README.md** is the human-facing overview — what the plugin does, how to install, skill table
- **CLAUDE.md** (this file) is the agent instruction set — conventions, boundaries, directory map
- **DECISIONS.md** logs architectural choices — add entries before implementing significant changes
- **ROADMAP.md** captures future directions — items flow to DECISIONS.md when evaluated
- **CHANGELOG.md** tracks evolution narratively — update after significant work sessions
- Skill-internal docs (like `convert/references/roadmap.md`) are scoped to that skill, not the whole plugin

## Agent Boundaries

### Do

- Read this file first on every session
- When adding new skills, follow the `convert` skill's structure (SKILL.md + references/ + scripts/)
- Prefer delegating to built-in Anthropic skills (`pdf`, `docx`, `pptx`, `xlsx`) before writing custom extractors
- Log decisions in DECISIONS.md before implementing structural changes
- Update CHANGELOG.md after significant work sessions
- Test new skills against real documents before shipping
- Bump the version in `.claude-plugin/plugin.json` for every release

### Don't

- Auto-commit changes — always show the diff first
- Hardcode assumptions about environment (RAM, installed tools) — probe at runtime
- Write helper scripts when an existing library or built-in skill would work
- Remove the deprecated `pdf-convert` skill until v0.4 (give users a migration window)
- Duplicate content between files — reference instead
- Bundle heavy dependencies at install time — use lazy loading on first skill invocation

## Design Principles

1. **Guides not rails** — Recipes, playbooks, and phase instructions are defaults, not mandates. Agents can deviate when they have specific reasons; deviations must be named for transparency. Over-prescription is itself a failure mode.

2. **Progressive disclosure** — Root files stay small (README, CLAUDE.md). Skill-specific details live in `skills/<name>/references/` and are only loaded when that skill is invoked. This follows Anthropic's Agent Skills three-level model (metadata → instructions → nested files).

3. **Dual-audience documentation** — README.md serves humans, CLAUDE.md serves agents. Don't collapse one into the other. Skill SKILL.md files are agent-facing; their references are agent-facing too. There's no human-facing skill documentation — that's what the README is for.

4. **Adaptive over prescriptive** — Skills should probe the environment and match source archetypes to recipes at runtime, not assume a fixed input format or a fixed execution environment. The `convert` skill is the canonical example.

5. **Graceful degradation** — When a preferred tool isn't available, fall back silently and record the quality downgrade in frontmatter. Never silently produce garbage; loudly flag failures that matter.

6. **Decisions as first-class artifacts** — Significant structural choices get logged in DECISIONS.md before implementation. This creates a searchable trail that survives memory loss.

7. **Source-grounded defaults** — Every convention should trace to a documented source or a specific lesson learned from real usage. No convention exists "because it seemed right."

## Key Skills Overview

### convert (primary skill, v0.3)

Adaptive document-to-markdown orchestrator. Five phases: Probe → Plan → Execute → Enrich → Verify. Seven-recipe catalogue. Six enrichment playbooks. Handles PDF, docx, pptx, epub, html, image. Replaces `pdf-convert`.

Entry point: `skills/convert/SKILL.md`.

### clip (v0.2)

Web-page-to-markdown via Defuddle. Strips ads/nav/chrome, saves clean markdown with YAML frontmatter. Unchanged from v0.2.

Entry point: `skills/clip/SKILL.md`.

### pdf-convert (DEPRECATED, v0.2)

Docling-first PDF converter. Deprecated in v0.3, will be removed in v0.4. Use `convert` instead.

Entry point: `skills/pdf-convert/SKILL.md` (contains deprecation notice).

## References

- [DECISIONS.md](DECISIONS.md) — architectural decision log
- [ROADMAP.md](ROADMAP.md) — future directions and inspiration
- [CHANGELOG.md](CHANGELOG.md) — narrative change history
- [README.md](README.md) — human-facing overview

<!-- Scaffold sources: Anthropic CLAUDE.md conventions, HumanLayer CLAUDE.md best practices, Anthropic Agent Skills architecture, agentic-scaffold-plugin v0.1.0 -->
