# md-superpowers

Markdown superpowers for knowledge gardens. A Claude Cowork plugin for web clipping, content ingestion, and reading management.

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `/clip` | "clip this", "save this page", "defuddle", paste a URL | Fetches a web page via Defuddle, strips ads/nav/chrome, saves clean markdown with YAML frontmatter |

## Dependencies

- **Node.js** (available in Cowork sandbox)
- **defuddle** npm package (auto-installed on first use each session)

## Output

Clipped files include YAML frontmatter (title, source, author, date, word count) followed by clean article markdown. Files are saved to contextually appropriate locations in the knowledge garden.

## Roadmap

Future skills to explore for this plugin. Each builds on the core clipping workflow to cover more of the content ingestion pipeline.

### pdf-convert

Convert PDFs to clean, searchable markdown using Docling (IBM's PDF parser) plus custom post-processing and verification scripts. Would use lazy dependency installation — `pip install docling` runs only when the skill is first invoked in a session, not on startup. Heavier than defuddle (~30-60s install) but only sessions that actually need PDF conversion pay the cost. The existing Claude Code skill and scripts (`tools/pdf_postprocess.py`, `tools/pdf_verify.py`) provide the foundation.

### process-inbox

Triage and route items from `ops/inbox/` into the appropriate knowledge directory. Reads frontmatter and content to suggest the right destination (readings, research, wisdom, etc.), applies any missing metadata, moves the file, and optionally triggers QMD indexing. This is the "second half" of the clipping workflow — currently done manually.

### research-clip

Research-aware variant of clipping. When working within a specific research domain, clips a URL directly into `research/<domain>/references/`, creates or updates a research log entry noting what was clipped and why, and cross-references `repos-and-tools.md` if the article mentions tracked tools. Combines clip + file + log in one action.

### QMD Integration

Bundle a QMD MCP server connection in the plugin's `.mcp.json` so clipped content can be immediately indexed and searchable without a separate `qmd update && qmd embed` step. Consideration: QMD is already configured at the workspace level, so bundling it here would duplicate the server definition. Worth exploring whether the plugin can reference the existing workspace-level MCP or whether it needs its own.

## License

MIT
