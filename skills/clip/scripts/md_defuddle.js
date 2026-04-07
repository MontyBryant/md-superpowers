#!/usr/bin/env node
/**
 * md_defuddle.js — Web clipper using Defuddle
 *
 * Usage:
 *   node tools/md_defuddle.js <url> [output_file]
 *
 * If output_file is omitted, prints to stdout.
 *
 * Output: clean markdown file with YAML frontmatter extracted from page metadata.
 */

const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

const url = process.argv[2];
const outputPath = process.argv[3];

if (!url) {
  console.error("Usage: node tools/md_defuddle.js <url> [output_file]");
  process.exit(1);
}

// Fetch and parse via defuddle CLI
let raw;
try {
  raw = execSync(`defuddle parse --json "${url}"`, {
    encoding: "utf8",
    timeout: 30000,
  });
} catch (e) {
  console.error("defuddle failed:", e.message);
  process.exit(1);
}

const data = JSON.parse(raw);

const today = new Date().toISOString().slice(0, 10);

// Build frontmatter fields
const title = data.title || "";
const description = data.description || "";
const domain = data.domain || "";
const author = data.author || "";
const site = data.site || "";
const published = data.published || "";
const language = data.language || "";
const wordCount = data.wordCount || 0;
const image = data.image || "";

const frontmatter = [
  "---",
  `title: "${title.replace(/"/g, '\\"')}"`,
  `source: ${url}`,
  `domain: ${domain}`,
  author ? `author: "${author.replace(/"/g, '\\"')}"` : null,
  site && site !== author ? `site: "${site.replace(/"/g, '\\"')}"` : null,
  description ? `description: "${description.replace(/"/g, '\\"')}"` : null,
  published ? `published: ${published}` : null,
  `clipped: ${today}`,
  language ? `language: ${language}` : null,
  wordCount ? `word_count: ${wordCount}` : null,
  image ? `image: ${image}` : null,
  "---",
]
  .filter(Boolean)
  .join("\n");

const content = data.contentMarkdown || data.content || "";
const output = `${frontmatter}\n\n# ${title}\n\n${content.trim()}\n`;

if (outputPath) {
  const dir = path.dirname(outputPath);
  if (dir && dir !== ".") fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(outputPath, output, "utf8");
  console.error(`Saved to ${outputPath}`);
} else {
  process.stdout.write(output);
}
