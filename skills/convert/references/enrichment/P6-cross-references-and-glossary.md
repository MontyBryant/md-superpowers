# P6 — Cross-references and glossary

For documents that introduce multiple proper nouns, acronyms, or concepts that other documents in the commons will want to link to, build a short glossary at the bottom of the converted file. Optional per-recipe — opt-in, not automatic.

## When to use

Apply P6 when the source contains:

- **Named initiatives, programs, or organisations** defined in the document and likely to appear elsewhere in the commons
- **Acronyms** defined for the first time (TFL, LFS, IPBES, REDD+, etc.)
- **Place names with specific context** (Ma̱c̓inux̌ʷ SFMA, Great Bear Rainforest, Costa Rica's Payment for Environmental Services scheme)
- **Technical terms** the document defines and uses repeatedly

## When NOT to use

Skip the glossary for:

- **Simple one-pagers** — the overhead isn't worth it
- **Documents that already contain a glossary in the source** — use the source's glossary verbatim as a section, don't write your own
- **Single-concept documents** — if the whole doc is about one thing, a glossary of one entry is silly
- **Academic papers** where terms are defined inline and don't need external linking

## Glossary format

At the bottom of the markdown file, under an H2 heading:

```markdown
## Glossary and cross-references

- **TFL (Tenured Forest Land)** — A land tenure arrangement where Indigenous or community stewards hold long-term rights to manage a forest. First introduced in slide 6.
- **LFS (Living Forest Standard)** — Ecological outcome methodology developed by the Kwaxala initiative. Defines what qualifies as regenerative forest management. First introduced in slide 9. → See also `research/methodologies/living-forest-standard.md` (if exists)
- **Catalytic Commitment Facility** — Project finance layer that underwrites individual TFL/LFS projects. First introduced in slide 9.
- **Living Forest Fund** — Catalytic capital wrapper that pools investor money for TFL/LFS projects. First introduced in slide 9.
- **Ma̱c̓inux̌ʷ SFMA** — The specific Special Forest Management Area where the first Kwaxala pilot is located. First introduced in slide 4.
```

## Entry format

Each entry:

1. **Term** in bold — the name, optionally with expansion in parentheses for acronyms
2. **Em dash**
3. **One-line definition** — what it is, functionally
4. **Location reference** — where it first appears in the doc (page, slide, section)
5. **Optional cross-reference** — `→ See also <path>` pointing to another commons file, if one exists

## Cross-references to other commons files

When you know a term connects to other work in the commons, add a forward reference. Use the skill's commons-awareness detection — if you're in a Bridging Worlds working tree, check for other files that reference the same term.

**How to check cheaply:** grep the working tree for the term. If matches exist, add a `→ See also` pointing to the most relevant match.

**How to handle forward references to files that don't exist yet:** if a term would likely get its own commons page in future but doesn't now, you can note it as aspirational: `→ (future) research/methodologies/living-forest-standard.md`. Use sparingly — don't invent links that aren't likely to be created.

## Selecting entries

For a typical document, 5–15 glossary entries is right. Signs you have too many:
- You're including every proper noun whether or not it's central
- You're defining terms that appear only once
- The glossary is longer than a page

Signs you have too few:
- Core concepts aren't listed
- A reader unfamiliar with the domain would still be lost
- Acronyms used repeatedly aren't defined

## Failure modes

- **Inventing definitions.** If the source doesn't define a term but uses it, either skip it or extract the definition carefully from context (and mark it as inferred).
- **Cross-referencing non-existent files.** Verify catches broken links — don't invent paths.
- **Duplicating the source's glossary.** If the source has one, use it, don't rewrite.
- **Glossary longer than the main content.** A sign you're over-doing it.

## Deviation guidance

- Skip entirely for `simple-onepager` — the overhead isn't justified
- Keep minimal for `academic-paper` — usually the terms are defined inline
- Expand fully for `institutional-report` and `book-longform` — these benefit most
- For `slide-deck-visual` — include the glossary by default because slide decks often introduce many named concepts without inline definitions
