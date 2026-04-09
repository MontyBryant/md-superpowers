# mdpowers-cowork

Markdown superpowers for knowledge gardens. A Claude Cowork plugin for adaptive document-to-markdown conversion and web clipping, optimised for AI-readable output.

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `/convert` | "convert", "pdf to markdown", "docx to markdown", "pptx to markdown", "slide deck to markdown", upload a document | Adaptively converts any document (PDF, docx, pptx, epub, html, image) into structured, AI-readable markdown — with diagrams → mermaid, comparisons → tables, per-recipe enrichment, and graceful engine fallback |
| `/clip` | "clip this", "save this page", "defuddle", paste a URL | Fetches a web page via Defuddle, strips ads/nav/chrome, saves clean markdown with YAML frontmatter |
| `/pdf-convert` | *(deprecated)* | **Deprecated in v0.3.** Use `/convert` instead. Will be removed in v0.4. |

## What makes `convert` different

`convert` isn't just another PDF-to-text extractor. It's an adaptive orchestrator that:

1. **Probes the source and environment** — file characteristics (type, layout, metadata), available tools (docling, marker, pymupdf, built-in Anthropic skills), and runtime constraints (RAM, disk)
2. **Matches the source to a recipe** — seven archetypes: slide deck, academic paper, institutional report, book, scanned doc, one-pager, hybrid-novel
3. **Picks the right engine** — prefers built-in Anthropic skills (`pdf`, `docx`, `pptx`, `xlsx`), falls back gracefully to docling, marker, pymupdf, or pandoc as the environment allows
4. **Enriches the output** — diagrams become mermaid, comparisons become tables, visuals get semantic descriptions, frontmatter gets populated per recipe, glossaries are built for documents with named concepts
5. **Verifies the result** — mechanical checks (asset refs resolve, frontmatter complete, no broken mermaid) plus recipe-specific success criteria
6. **Adapts the planning ceremony to the document** — tight budget for simple files (no ceremony), standard budget for most documents (inline narration), deep budget for novel or complex sources (plan artifact + user review before execution)

The core design principle is "guides not rails": recipes and playbooks are defaults, not mandates. Agents can deviate when they have specific reasons, and deviations are named in the narration so they're visible.

See [`skills/convert/SKILL.md`](skills/convert/SKILL.md) for the full design, and [`DECISIONS.md`](DECISIONS.md) for the reasoning behind this architecture.

## Dependencies

All dependencies use lazy installation — they're only probed when a skill is first invoked in a session, not at plugin startup.

| Skill | Dependency | When needed | Install method |
|-------|-----------|-------------|----------------|
| `/convert` | Built-in `pdf`/`docx`/`pptx` skills | Always preferred | Native (no install) |
| `/convert` | pymupdf | Universal fallback for PDF | `pip install pymupdf --break-system-packages` |
| `/convert` | pandoc | docx, html, epub | `apt install pandoc` or `brew install pandoc` |
| `/convert` | docling (optional) | Claude Code environments with ≥6GB RAM | `pip install docling --break-system-packages` |
| `/convert` | marker (optional) | Claude Code environments with GPU/beefy CPU | `pip install marker-pdf --break-system-packages` |
| `/clip` | defuddle (npm) | Always | `npm install -g defuddle` |

All skills require **Node.js** and **Python**, which are available in the Cowork sandbox.

## Project Structure

```
mdpowers-plugin/
├── README.md                       # this file — human-facing overview
├── CLAUDE.md                       # agent instruction set
├── DECISIONS.md                    # architectural decision log
├── ROADMAP.md                      # future directions
├── CHANGELOG.md                    # narrative change history
├── .claude-plugin/plugin.json      # plugin manifest
├── .claude/settings.local.json     # Claude Code settings
└── skills/
    ├── convert/                    # adaptive document-to-markdown (v0.3)
    ├── clip/                       # web-page-to-markdown via Defuddle
    └── pdf-convert/                # DEPRECATED — removed in v0.4
```

## Design Principles

This plugin inherits the agentic-scaffold design principles. In brief:

1. **Guides not rails** — Recipes, playbooks, and phase instructions are defaults; agents can deviate with reason. Over-prescription is itself a failure mode.
2. **Progressive disclosure** — Root docs stay small; skill-specific detail lives in `skills/<name>/references/` and loads on demand.
3. **Dual-audience documentation** — README.md for humans, CLAUDE.md for agents. Don't collapse them.
4. **Adaptive over prescriptive** — Probe environment and source at runtime; don't assume fixed inputs or fixed tools.
5. **Graceful degradation** — Fall back silently when tools are missing; record quality downgrades in frontmatter. Never silently produce garbage.
6. **Decisions as first-class artifacts** — Significant choices get logged in DECISIONS.md before implementation.
7. **Source-grounded defaults** — Every convention traces to a documented source or a lesson from real usage.

The full rationale for each principle is in [`CLAUDE.md`](CLAUDE.md).

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned work and future ideas. Highlights:

- Validating `convert` against real documents across all seven recipe archetypes
- Removing the deprecated `pdf-convert` skill in v0.4
- New playbooks for equation handling (P7), citation parsing (P8), figure-caption grounding (P9)
- New recipes for annual reports and legal contracts
- `process-inbox` and `research-clip` skills for tighter integration with knowledge garden workflows

## Contributing

Contributions welcome. Before making structural changes:

1. Read [CLAUDE.md](CLAUDE.md) for conventions and boundaries
2. Check [DECISIONS.md](DECISIONS.md) for prior architectural choices
3. Log new decisions before implementing them
4. Follow the skill-authoring conventions in CLAUDE.md
5. Update CHANGELOG.md after significant work sessions

## License

MIT

---

*This plugin uses the [agentic scaffold](https://github.com/montymerlin/agentic-scaffold) pattern for AI-assisted development.*
