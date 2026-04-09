# Decisions — mdpowers-cowork

Architectural decisions for the mdpowers-cowork plugin, logged in a lightweight ADR (Architectural Decision Record) format. Each entry captures the context, the choice made, and its consequences — creating a searchable trail that survives memory loss.

**Format:** Each decision gets a sequential number, a status, and four sections: Context, Decision, Consequences, and (optionally) Alternatives Considered.

---

## Decision 001: Adopted agentic scaffold

**Status:** Accepted
**Date:** 2026-04-09

**Context:** The plugin was growing from a single-purpose PDF converter into a broader markdown-ingestion toolkit. Without explicit conventions, future skill authoring would drift inconsistently — each skill would make its own decisions about file layout, reference structure, frontmatter contracts, and deviation guidance. A scaffold of meta-documentation files establishes shared conventions and gives future contributors (human or agent) a clear map of how the plugin is organised.

**Decision:** Adopted the Agentic Scaffold pattern — a coordinated set of top-level files (CLAUDE.md, README.md, DECISIONS.md, ROADMAP.md, CHANGELOG.md) alongside the existing `skills/` directory. This mirrors the structure of `agentic-scaffold-plugin` and `bridging-worlds`.

**Consequences:**
- New skills follow a shared authoring convention documented in CLAUDE.md
- Structural decisions have a home (this file) rather than being buried in commits
- Future direction is visible in ROADMAP.md rather than lost in notes
- The plugin's evolution is narrated in CHANGELOG.md instead of inferred from git log
- Adds five small meta files; each serves a distinct audience

**Alternatives Considered:**
- No scaffold (README only) — worked at v0.2 scale, insufficient now that the plugin has multiple skills and an active roadmap
- Heavier framework (full ADR tooling, multiple config files) — premature
- Embed everything in README — conflates human and agent audiences, README becomes unmaintainable

---

## Decision 002: Replaced pdf-convert with adaptive convert skill

**Status:** Accepted
**Date:** 2026-04-09

**Context:** The original `pdf-convert` skill was docling-first and assumed a Claude Code + macOS environment with ample RAM. In Cowork sandbox environments (3.8GB RAM, ephemeral), docling is SIGKILL'd on any real PDF due to OOM. The skill also had no semantic enrichment — it produced plain text extraction without structured representations of diagrams, comparisons, or visual content. A real-world test on the Kwaxala Overview 2026 pitch deck made both limitations painfully visible: the skill couldn't run at all in the available environment, and even when fallback extraction succeeded, the output was a flat text dump that an AI couldn't meaningfully reason over.

Beyond PDFs specifically, users also wanted consistent treatment for docx, pptx, epub, and other document types. Writing a separate skill per format would fragment the plugin and duplicate effort.

**Decision:** Replaced `pdf-convert` with a new `convert` skill that:

1. Handles any document type (PDF, docx, pptx, epub, html, image) through a single entry point
2. Probes the source and environment at runtime, matching the source to one of seven recipe archetypes and picking a viable engine from an ordered preference list
3. Follows a five-phase workflow (Probe → Plan → Execute → Enrich → Verify) with adaptive planning budget (tight / standard / deep)
4. Delegates to built-in Anthropic skills (`pdf`, `docx`, `pptx`, `xlsx`) as first-choice engines, with graceful degradation to pymupdf, pandoc, and other universal fallbacks
5. Applies six enrichment playbooks (diagrams→mermaid, comparisons→tables, images, descriptions, frontmatter, glossary) tuned per recipe
6. Operates under a "guides not rails" principle — recipes and playbooks are defaults, deviation is a normal move, transparency is the safety valve

`pdf-convert` is kept on disk with a deprecation notice and will be removed in v0.4, giving users one release cycle to migrate.

**Consequences:**
- The plugin now handles a much broader input surface (not just PDFs)
- Environment-specific failures become graceful degradations instead of hard blocks
- Output quality is dramatically better for complex sources (slide decks, institutional reports, books)
- The plugin now has a documented authoring convention that future skills can follow
- Maintenance burden: the convert skill is ~1,900 lines across 12 files — significantly more than pdf-convert's ~200 lines, but most of that is reusable catalogue content
- Users need to update muscle memory from `/pdf-convert` to `/convert`

**Alternatives Considered:**

- **Fix pdf-convert in place** — smaller change, but wouldn't address the enrichment gap, the multi-format need, or the underlying architectural mismatch between "assume docling works" and the realities of the Cowork sandbox
- **Build a multi-skill suite** (`convert-plan`, `convert-execute`, `convert-verify`) — more modular but fragmented for no current benefit; folded the phase structure inside a single skill as internal stages, with the option to split later if usage demands it
- **Thin router skill** — smallest change, all intelligence in prose instructions the agent reads each time. Rejected because it provided no mechanism for the adaptive planning budget and no place for the enrichment playbooks to live

---

## Decision 003: "Guides not rails" as project-wide principle

**Status:** Accepted
**Date:** 2026-04-09

**Context:** During the design of the `convert` skill, a tension emerged between prescriptive instructions (catalogue-driven, deterministic, easy to verify) and adaptive judgment (agent-driven, context-sensitive, harder to verify but often producing better output). Over-prescription had been a failure mode of `pdf-convert` — it assumed a specific engine and failed when that assumption was wrong. Under-prescription would risk chaos, with every invocation producing inconsistent results.

**Decision:** Established "guides not rails" as a project-wide design principle. Recipes, playbooks, and phase instructions are defaults the agent can adapt from when a specific document warrants it. Deviations must be named in the agent's narration ("treating this as X but skipping Y because Z"). Hard rails are listed explicitly in `skills/convert/references/anti-patterns.md` — everything else is soft.

The principle applies to all future skills in the plugin, not just `convert`.

**Consequences:**
- Recipes can capture good defaults without becoming bureaucratic
- Agents are trusted to make judgment calls, with transparency as the accountability mechanism
- Future skill authors must explicitly document which rails are hard and which are soft
- Verification is outcome-based (success criteria) not process-based (did you follow the steps)

**Alternatives Considered:**
- **Fully prescriptive** (every step mandatory) — simpler to verify, but brittle in exactly the way pdf-convert was brittle
- **Fully adaptive** (no catalogue) — each conversion starts from scratch; wastes effort and produces inconsistent results

---

## Decision 004: Prefer built-in Anthropic skills as first-choice engines

**Status:** Accepted
**Date:** 2026-04-09

**Context:** Anthropic ships built-in skills for PDF, docx, pptx, and xlsx handling. These are maintained by the people who trained the model and receive updates tied to the model's capabilities. Writing custom extractors duplicates effort and produces tools that inevitably fall behind the built-ins. At the same time, the built-ins don't cover every environment (they may not be available in all contexts) and don't handle every edge case (specialised enrichment, recipe-specific output shapes).

**Decision:** The `convert` skill (and any future mdpowers skills handling document formats) will prefer built-in Anthropic skills as the first-choice engine in their preference lists. Custom or third-party tools (docling, marker, pymupdf, pandoc) are fallbacks used when the built-in isn't available or doesn't meet the recipe's needs.

**Consequences:**
- Less duplicated effort — mdpowers focuses on orchestration, enrichment, and recipes rather than re-implementing extraction
- Output benefits from ongoing Anthropic maintenance of the built-in skills
- The plugin is lighter-weight and easier to maintain
- Graceful degradation path is still necessary for environments without the built-ins

**Alternatives Considered:**
- **Custom-first** — maximum control, but loses the benefit of maintained tools and duplicates work
- **Built-in-only** — simpler but breaks in environments without the built-ins, and doesn't handle edge cases that need custom enrichment

---

<!-- Scaffold sources: Michael Nygard ADR proposal (2011), Keeling & Runde sustainable ADRs (IEEE Software), agentic-scaffold-plugin v0.1.0 -->
