# P4 — Semantic descriptions

How to write the prose description that accompanies every non-decorative visual. This is the AI-readability bridge — the thing that lets an agent understand the content of a visual without re-parsing the image.

## The contract

Every non-decorative visual (diagram, figure, chart, meaningful photo) in the output gets a 2–4 sentence prose description placed immediately after the image reference.

```markdown
![Slide 9: The Kwaxala four-layer stack](./slides/slide-09.jpg)

**The four-layer Kwaxala architecture.** Finance flows down the stack from
the Living Forest Fund through a Catalytic Commitment Facility, evaluated
against the Living Forest Standard, and lands as regenerative management of
Tenured Forest Land. Ecological outcomes flow back up: verified outcomes
from TFL feed the standard's evidence base, which validates the facility's
theses, building investor confidence in the fund.
```

## What a good description includes

- **Subject**: what the visual depicts (one line, usually in bold at the start)
- **Key elements**: the important components, labels, or entities visible
- **Key relationships**: how the elements relate — flows, connections, hierarchies, comparisons
- **Why it matters**: the role this visual plays in the surrounding content

## Length guidance

- **Simple photos / scenes**: 1 sentence is enough
- **Standard diagrams / figures**: 2–4 sentences
- **Dense infographics**: up to a paragraph (but consider whether a table or mermaid would do better)
- **Charts / data visualisations**: 2–3 sentences covering what's shown + any notable patterns

Err on the side of shorter. If you need more than a paragraph, the visual is probably better represented as structured data (table or mermaid), not prose.

## Tone and voice

- **Factual**, not interpretive. Describe what's there, not what you think it means (interpretation belongs in the surrounding content, not the description).
- **Present tense**: "The diagram shows..." not "The diagram showed..."
- **Third person**: don't use "I see..." or "you can see..."
- **Concrete**: name specific elements by the labels in the visual, not abstractions

**Good:** "The chart shows carbon offset issuance from 2014–2024, rising from under 100M credits per year to over 700M by 2023 before a slight decline in 2024."

**Bad:** "The chart shows how carbon markets have grown a lot recently." (Too vague — no numbers, no timeframe.)

**Bad:** "The chart shows the concerning rise of carbon markets, raising questions about greenwashing." (Interpretive — that's analysis, not description.)

## Don't re-describe what's obvious from surrounding text

If the paragraph above the image already walks through the flowchart step by step, the description shouldn't duplicate it. Instead, describe what the visual *adds* — usually the visual relationships that are hard to convey in prose (the spatial layout, the arrows, the emphasis).

Example:

```markdown
The Kwaxala stack has four layers. Finance flows down from the Living
Forest Fund, through a Catalytic Commitment Facility that underwrites
individual projects, evaluated against the Living Forest Standard, and
lands on Tenured Forest Land.

![Slide 9: The Kwaxala stack](./slides/slide-09.jpg)

**Stack diagram emphasising the two-way flow.** The visual makes explicit
that capital and outcomes move in opposite directions — dashed lines for
outcomes feeding back up, solid arrows for capital flowing down — which
frames the whole architecture as a closed loop rather than a one-way pipe.
```

The description doesn't re-explain what the stack is (the prose already did that). It adds what the visual uniquely conveys — the two-way flow being the key design insight.

## Worked examples

**Photo (minimal):**
```markdown
![Old-growth forest in the Ma̱c̓inux̌ʷ SFMA](./slides/slide-04.jpg)

**Old-growth forest in the Ma̱c̓inux̌ʷ Special Forest Management Area.** Large
cedar and spruce, multi-layered canopy, mossy understorey — the kind of
stand the Kwaxala initiative aims to keep standing.
```

**Bar chart:**
```markdown
![Figure 3: Monthly credit issuance 2014-2024](./assets/fig-03.png)

**Monthly voluntary carbon credit issuance, 2014–2024.** Issuance rises
from ~5M credits/month in 2014 to peaks above 60M/month in 2023, with
visible volatility and a notable drop in Q4 2024. The chart annotates
three events: the 2018 methodology update, the 2021 ICVCM announcement,
and the 2023 integrity reporting wave.
```

**System diagram:**
```markdown
![System architecture: Kwaxala finance-and-outcome loop](./slides/slide-14.jpg)

**Single-project finance-and-outcome loop.** Shows how a single Kwaxala
project receives capital from the fund via the facility, generates
ecological and cultural outcomes through TFL management, and produces
verified credits that flow back to investors. The diagram emphasises that
verification happens independently via the Living Forest Standard, not
via the facility itself.
```

## Failure modes

- **Vague descriptions.** "This is a diagram of the system." — useless. Describe the actual system.
- **Interpretive overreach.** Adding your own analysis. Stay factual.
- **Redundant with surrounding text.** Don't repeat what the paragraph above already said.
- **Missing the point.** A description that lists components but misses the key relationship or message. Lead with the insight, fill in the parts.
- **Over-long.** If you're writing a paragraph to describe a 4-box diagram, either the diagram is more complex than it looks (in which case use mermaid/table) or you're overdoing it.

## Deviation guidance

- For decorative images (backgrounds, flourishes, stock photography for visual interest), skip the description entirely — minimal alt text is enough
- For images where the description would need to be longer than 4 sentences, use structured forms (P1 mermaid, P2 tables) instead
- When the source already provides a caption, use it as the starting point for your description — but expand it to cover the "why it matters" dimension
