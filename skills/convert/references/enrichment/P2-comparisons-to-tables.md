# P2 — Comparisons to tables

For any before/after, this/that, extractive/regenerative, traditional/alternative framing — extract to a markdown table. Tables are the AI-readable form of comparison; bullet lists lose the correspondence between attributes.

## When to use

Apply P2 when the source contains:

- **Before/after comparisons** (pilot economics, policy reform, transformation narratives)
- **Paired framings** (extractive vs regenerative, centralised vs decentralised, legacy vs emerging)
- **Three-way or N-way comparisons** (multiple methodologies, options, scenarios)
- **Feature matrices** (products, approaches, frameworks with shared attributes)
- **Trade-off analyses** (pros/cons across multiple dimensions)
- **Two-column slide layouts** that are implicitly comparisons

## How to detect comparisons in prose

Signal phrases to watch for:
- "Unlike X, Y does Z"
- "Whereas X..., Y..."
- "Traditional/conventional X is Y; the alternative is Z"
- Parallel bullet lists (two bullet lists with the same number of items and parallel structure)
- Two-column layouts in slides or reports
- Section pairs ("The old approach" / "The new approach")
- Diagrams showing transformation arrows between two states

## Table structure

**Two-way comparison (most common):**

```markdown
| Dimension | Option A | Option B |
|---|---|---|
| Approach | ... | ... |
| Outcomes | ... | ... |
| Limitations | ... | ... |
```

Column order matters: put the "from" or "traditional" or "baseline" column second (left-to-right reads as "dimension, baseline, alternative").

Actually, convention varies — use whatever the source uses. If the source goes "extractive → regenerative" left to right, match that.

**Three-way and N-way comparisons:**

Same structure, more columns. Keep column headers short; expand details in cells.

**Preserving nuance that doesn't fit a cell:**

Use footnote-style annotations below the table:

```markdown
| Dimension | Option A | Option B |
|---|---|---|
| Cost | Low | High¹ |
| Quality | Medium | High |

¹ Cost depends significantly on scale — see source section 3.2 for the full curve.
```

## What not to table

- **Lists of features for one thing.** That's a list, not a comparison. Keep as bullets.
- **Comparisons where one side is much richer than the other.** If A has 10 attributes and B has 2, forcing a table makes B look artificially thin. Prose it.
- **Comparisons where the source intentionally uses prose for nuance.** Sometimes the author's point is that the comparison *can't* be neatly tabled. Respect that.

## Worked example (from Kwaxala, slide 11 — extractive vs regenerative tenure)

**Source:** A two-column slide with "Extractive Tenure" on the left, "Regenerative Tenure" on the right, and parallel bullet points covering ownership model, time horizon, success metrics, and stakeholder relationships.

**Output:**

```markdown
| Dimension | Extractive Tenure | Regenerative Tenure |
|---|---|---|
| Ownership model | Fee simple, individual/corporate | Trust-based, community/Indigenous-held |
| Time horizon | Quarterly to decadal | Multi-generational |
| Success metrics | Extraction volume, ROI | Ecosystem health, cultural continuity |
| Stakeholder relationships | Transactional | Relational, reciprocal |
| Exit optionality | Sell/liquidate | Steward or transfer to aligned successor |
```

Notice the table preserves the row-by-row correspondence that would be lost in parallel bullets.

## Failure modes

- **Forcing a table when the source is actually a single enriched framing.** Look for real parallel structure, not surface similarity.
- **Losing hedging language.** "Usually X but sometimes Y" becomes "X" in a cell and loses the hedge. Use footnotes.
- **Inventing comparisons the source doesn't make.** Don't table things the source author didn't pair.
- **Over-granular tables.** 15-row comparisons are usually better as narrative with a few summary tables.

## Deviation guidance

Skip tables when:
- The comparison is already crystal clear in 2-3 sentences of prose
- The source uses a visual format (Venn diagram, spectrum, matrix) that loses information when flattened to rows and columns
- The comparison is between more than ~5 options — consider splitting into multiple tables or a different structure entirely
