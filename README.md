# md-superpowers

Markdown superpowers for knowledge gardens. A Claude Cowork plugin for web clipping, content ingestion, and reading management.

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `/clip` | "clip this", "save this page", "defuddle", paste a URL | Fetches a web page via Defuddle, strips ads/nav/chrome, saves clean markdown with YAML frontmatter |
| `/pdf-convert` | "convert pdf", "pdf to markdown", "docling", upload a PDF | Converts PDFs to clean markdown via Docling with automated post-processing and quality review |

## Dependencies

All dependencies use lazy installation — they're only installed when the relevant skill is first invoked in a session, not on startup.

| Skill | Dependency | Install time | Method |
|-------|-----------|-------------|--------|
| `/clip` | defuddle (npm) | ~2s | `npm install -g defuddle` |
| `/pdf-convert` | docling (pip) | ~30-60s | `pip install docling` |

Both require **Node.js** and **Python**, which are available in the Cowork sandbox.

## Output

Both skills produce clean markdown with contextually appropriate file placement in the knowledge garden. `/clip` adds YAML frontmatter (title, source, author, date, word count). `/pdf-convert` produces markdown with referenced images and runs automated post-processing and verification.

## Roadmap

Future skills to explore. Each builds on the core workflow to cover more of the content ingestion pipeline.

### process-inbox

Triage and route items from `ops/inbox/` into the appropriate knowledge directory. Reads frontmatter and content to suggest the right destination (readings, research, wisdom, etc.), applies any missing metadata, moves the file, and optionally triggers QMD indexing. This is the "second half" of the clipping workflow — currently done manually.

### research-clip

Research-aware variant of clipping. When working within a specific research domain, clips a URL directly into `research/<domain>/references/`, creates or updates a research log entry noting what was clipped and why, and cross-references `repos-and-tools.md` if the article mentions tracked tools. Combines clip + file + log in one action.

### QMD Integration

Bundle a QMD MCP server connection in the plugin's `.mcp.json` so clipped content can be immediately indexed and searchable without a separate `qmd update && qmd embed` step. Consideration: QMD is already configured at the workspace level, so bundling it here would duplicate the server definition. Worth exploring whether the plugin can reference the existing workspace-level MCP or whether it needs its own.

## License

MIT
