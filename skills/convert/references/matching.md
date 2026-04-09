# Recipe matching rubric

How Probe picks a recipe. This is a scoring rubric, not a decision tree — the highest-scoring recipe wins if it scores ≥5, otherwise fall through to `hybrid-novel`.

## The scoring model

Each recipe has a set of signals. Each signal scores 0–3:
- **0** — signal is absent or contradicts this recipe
- **1** — signal is weakly suggestive
- **2** — signal is clearly present
- **3** — signal is strong and distinctive

Sum the signal scores per recipe. The recipe with the highest total wins if the total is ≥5.

**Tie-breaking:** If two recipes tie within 1 point, prefer the more specific recipe. Specificity order (most → least specific): `scanned-document` > `book-longform` > `slide-deck-visual` > `academic-paper` > `institutional-report` > `simple-onepager` > `hybrid-novel`.

**Fall-through:** If no recipe scores ≥5, use `hybrid-novel` and escalate to deep budget. This includes cases where multiple recipes score 3-4 each (suggesting the document is a hybrid).

## Signals per recipe

### slide-deck-visual

- Widescreen aspect ratio (>1.3:1 page dimensions): **3**
- Native pptx file: **3** (strong — very high confidence)
- Low text density (<150 words per page average): **2**
- High image/diagram density (≥1 significant visual per page): **2**
- Page count ≤60: **1**
- Single-column layout per page: **1**
- File size ≥3MB with low text extraction (lots of images): **1**
- Large font headings dominating pages: **1**

### academic-paper

- DOI detected in first 2 pages: **3**
- Abstract heading present: **3**
- References/Bibliography section detected: **2**
- 2-column body layout: **2**
- Author block with affiliations on first page: **2**
- Journal name or "preprint" indicator visible: **2**
- Figure/Table captions in standard academic format ("Figure 1.", "Table 1."): **1**
- Page count 8-50: **1**

### institutional-report

- Publisher name in front matter (UN/FAO/IPBES/think tank): **3**
- Executive summary heading present: **2**
- ToC with chapter structure: **2**
- Heavy front matter (cover, foreword, acknowledgments): **2**
- Page count 20-300: **1**
- Many callout boxes / sidebars: **1**
- Series name or report number: **1**
- Contributor list (multiple authors, editors): **1**

### book-longform

- ISBN detected: **3**
- Chapter-based ToC with ≥5 chapters: **3**
- Page count >80: **2**
- Publisher in metadata: **2**
- Preface/Foreword section: **1**
- Sustained narrative prose (low structural markup): **1**
- epub file type: **3** (books are the dominant epub use case)

### scanned-document

- Text layer missing or empty: **3**
- Text extraction yields garbage (high ratio of glyph IDs, no real words): **3**
- Page images are large and dense: **2**
- OCR markers visible in metadata: **1**
- Scan artifacts detectable (skew, JPEG noise on text): **1**

### simple-onepager

- Page count ≤3: **3**
- Single column: **2**
- No ToC, no abstract, no references section: **2**
- Minimal structural markup (flat heading hierarchy): **1**
- File size <500KB: **1**
- Text-heavy (high word count per page): **1**

### hybrid-novel

No positive signals — this is the fall-through. Scored as 0 always. Only selected if no other recipe reaches 5.

## Worked examples

**Example 1 — Kwaxala Overview 2026.pdf (the session that motivated this design):**
- 25-page PDF, widescreen aspect ratio, ~0.3 text-image ratio
- `slide-deck-visual`: widescreen (3) + low text density (2) + high image density (2) + page count (1) + single column (1) = **9** ✓
- `institutional-report`: ToC none (0) + exec summary none (0) + 0 + 0 + page count not in range (0) = **0**
- `academic-paper`: no DOI (0) + no abstract (0) + no refs (0) + no 2-col (0) = **0**
- Winner: `slide-deck-visual` with 9 points.

**Example 2 — A Frontiers in Ecology journal article:**
- 14-page PDF, 2-column, DOI, abstract, refs
- `academic-paper`: DOI (3) + abstract (3) + refs (2) + 2-col (2) + authors (2) + journal (2) + captions (1) + page count (1) = **16** ✓
- `institutional-report`: 0 + 0 + 0 + 0 = **0**
- Winner: `academic-paper` with 16 points.

**Example 3 — A 180-page IPBES thematic assessment:**
- PDF, heavy front matter, exec summary, ToC, publisher = IPBES
- `institutional-report`: publisher (3) + exec summary (2) + ToC (2) + front matter (2) + page count (1) + callouts (1) + series (1) = **12** ✓
- `book-longform`: ISBN? maybe (0-3) + chapters (3) + page count (2) + publisher (2) + preface (1) = **8-11**
- Tie-ish — winner is `institutional-report` because it's more specific to this content type. But if the IPBES report has an ISBN and is formatted as a book, escalate to deep planning and consider hybrid treatment.

**Example 4 — A 5-page policy brief with no clear structure:**
- `simple-onepager`: page count (3) + single col (2) + no ToC (2) + minimal markup (1) + file size (1) + text-heavy (1) = **10** — but wait, page count is 5, not ≤3, so the (3) becomes (1 or 0)
- Recalculated: page count weak (1) + single col (2) + no ToC (2) + minimal markup (1) + text-heavy (1) = **7** ✓
- Winner: `simple-onepager` with 7 points.

**Example 5 — A hybrid pitch-deck-that-is-actually-a-report:**
- 40-page PDF, widescreen, but dense text, has an exec summary, publisher visible
- `slide-deck-visual`: widescreen (3) + low text density (0 — it's text-dense) + image density (1) + page count (1) = **5** (just barely)
- `institutional-report`: publisher (3) + exec summary (2) + no ToC (0) + front matter (1) = **6** ✓
- Winner: `institutional-report` with 6 points, but both are close — consider escalating to deep budget because the format is unusual.

## When to override the rubric

The rubric is a default, not a mandate (same principle as the rest of the skill). You can override if:

1. **You have direct evidence the rubric got it wrong** — e.g. the file name or user's description makes the archetype obvious despite low signal scores. State the override in narration: "Rubric scored this as `simple-onepager` but the filename says `kwaxala-overview-2026.pdf` and the user called it a pitch deck, so treating as `slide-deck-visual`."

2. **The winning recipe scored barely above threshold (5-6)** and the document feels hybrid. Escalate to deep budget and consider `hybrid-novel`.

3. **The user has already named the recipe** — if the user says "convert this academic paper", use `academic-paper` even if the rubric disagrees, and note the discrepancy in the Verify report so the rubric can be improved.

Log overrides in the Verify report so the matching model can be tuned over time.
