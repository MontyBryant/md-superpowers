"""
Post-conversion quality verification for PDF-to-markdown files.

Generates a structured quality report flagging issues that need human review.
Run after pdf_postprocess.py to catch remaining problems.

Usage:
    python tools/pdf_verify.py <md_file>
    python tools/pdf_verify.py --batch <directory>
    python tools/pdf_verify.py --batch <directory> --reference-dir <pdf_dir>
"""

import argparse
import re
from pathlib import Path


class Issue:
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"

    def __init__(self, severity, category, message, line=None, sample=None):
        self.severity = severity
        self.category = category
        self.message = message
        self.line = line
        self.sample = sample

    def __str__(self):
        loc = f" (line {self.line})" if self.line else ""
        sample_str = f'\n    > {self.sample[:120]}' if self.sample else ""
        return f"  [{self.severity}] {self.category}: {self.message}{loc}{sample_str}"


def verify(md_path: Path, pdf_path: Path = None) -> dict:
    """Run all verification checks on a converted markdown file."""
    content = md_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    issues = []

    # --- Size and content checks ---
    word_count = len(content.split())
    line_count = len(lines)
    non_blank_lines = sum(1 for l in lines if l.strip())

    if pdf_path and pdf_path.exists():
        pdf_size_kb = pdf_path.stat().st_size / 1024
        md_size_kb = md_path.stat().st_size / 1024
        ratio = md_size_kb / pdf_size_kb if pdf_size_kb > 0 else 0
        # Size ratio is unreliable for image-heavy PDFs (reports, books with
        # illustrations). A 10MB design-heavy PDF with 5k words of text will
        # have a ~1% ratio — that's normal. Only flag when combined with other
        # signals like low word count or glyph artifacts.
        if ratio < 0.05:
            issues.append(Issue(
                Issue.INFO, "Size Ratio",
                f"Markdown is {ratio:.1%} of PDF size ({md_size_kb:.0f}KB vs {pdf_size_kb:.0f}KB). "
                "Normal for image-heavy PDFs. Check word count and content below.",
            ))

    if word_count < 200:
        issues.append(Issue(
            Issue.CRITICAL, "Low Content",
            f"Only {word_count} words. Document may have irrecoverable text (custom font encoding).",
        ))
    elif word_count < 500:
        issues.append(Issue(
            Issue.WARNING, "Low Content",
            f"Only {word_count} words — verify this matches the source PDF scope.",
        ))

    # --- Content density (is there real prose or just headings/images?) ---
    content_lines = [l for l in lines if l.strip() and
                     not l.strip().startswith('#') and
                     not l.strip().startswith('!') and
                     not l.strip().startswith('|') and
                     not l.strip().startswith('---')]
    prose_lines = [l for l in content_lines if len(l.strip()) > 40]
    prose_ratio = len(prose_lines) / max(non_blank_lines, 1)

    if prose_ratio < 0.15 and word_count > 200:
        issues.append(Issue(
            Issue.WARNING, "Low Prose Density",
            f"Only {prose_ratio:.0%} of non-blank lines are prose (>40 chars). "
            "Document may be mostly headings/fragments. Consider --force-ocr.",
        ))

    # Words-per-content-line: healthy documents typically have 15+ words per
    # non-blank line. Very low values suggest fragmentary extraction.
    words_per_line = word_count / max(non_blank_lines, 1)
    if words_per_line < 8 and word_count > 300:
        issues.append(Issue(
            Issue.WARNING, "Fragmentary Text",
            f"Average {words_per_line:.1f} words per non-blank line — text may be fragmentary.",
        ))

    # --- Glyph ID remnants ---
    glyph_matches = re.findall(r'/gid\d{5}', content)
    if glyph_matches:
        issues.append(Issue(
            Issue.CRITICAL, "Glyph IDs",
            f"Found {len(glyph_matches)} unresolved /gidXXXXX references. Post-processor may not have run.",
        ))

    # --- Unicode ligature remnants ---
    ligature_matches = re.findall(r'/uni[0-9A-Fa-f]{4}', content)
    if ligature_matches:
        issues.append(Issue(
            Issue.WARNING, "Ligatures",
            f"Found {len(ligature_matches)} unresolved /uniXXXX references.",
            sample=ligature_matches[0]
        ))

    # --- Heading structure ---
    headings = [(i+1, line) for i, line in enumerate(lines) if re.match(r'^#{1,6}\s', line)]
    h1_count = sum(1 for _, h in headings if h.startswith('# ') and not h.startswith('## '))
    if h1_count == 0 and headings:
        issues.append(Issue(
            Issue.WARNING, "Headings",
            "No H1 heading found. Document may be missing its title.",
        ))
    elif h1_count > 3:
        issues.append(Issue(
            Issue.WARNING, "Headings",
            f"Found {h1_count} H1 headings — check if heading hierarchy is flat.",
        ))

    all_same_level = len(set(h.split(' ')[0] for _, h in headings)) == 1 if len(headings) > 3 else False
    if all_same_level and len(headings) > 5:
        issues.append(Issue(
            Issue.WARNING, "Flat Hierarchy",
            f"All {len(headings)} headings are the same level. Hierarchy may not have been fixed.",
        ))

    # False headings: headings that look like sentences
    for ln, h in headings:
        text = re.sub(r'^#{1,6}\s+', '', h)
        if len(text) > 120:
            issues.append(Issue(
                Issue.WARNING, "Long Heading",
                f"Heading is {len(text)} chars — may be a paragraph incorrectly styled as heading.",
                line=ln, sample=text
            ))

    # --- Broken tables ---
    table_blocks = []
    i = 0
    while i < len(lines):
        if lines[i].strip().startswith('|'):
            start = i
            while i < len(lines) and lines[i].strip().startswith('|'):
                i += 1
            table_blocks.append((start+1, i))
        else:
            i += 1

    for start_ln, end_ln in table_blocks:
        block = lines[start_ln-1:end_ln]
        empty_cells = sum(
            1 for line in block
            if re.match(r'^\|[\s|]*\|$', line.strip()) and not re.search(r'[a-zA-Z0-9]', line)
        )
        if empty_cells > len(block) * 0.5 and len(block) > 3:
            issues.append(Issue(
                Issue.WARNING, "Empty Table",
                f"Table has {empty_cells}/{len(block)} empty rows.",
                line=start_ln,
            ))

    # --- Image references ---
    img_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
    broken_images = []
    for alt, img_path in img_refs:
        full_path = md_path.parent / img_path
        if not full_path.exists():
            broken_images.append((img_path, None))
    if broken_images:
        issues.append(Issue(
            Issue.WARNING, "Broken Images",
            f"{len(broken_images)} image reference(s) point to missing files.",
            sample=broken_images[0][0]
        ))

    # --- Base64 embedded images ---
    base64_count = len(re.findall(r'!\[.*?\]\(data:image/', content))
    if base64_count:
        issues.append(Issue(
            Issue.CRITICAL, "Base64 Images",
            f"{base64_count} image(s) embedded as base64. Re-convert with --image-export-mode referenced.",
        ))

    # --- Stray artifacts ---
    lone_escapes = sum(1 for l in lines if l.strip() in ('\\_', '\\'))
    if lone_escapes > 2:
        issues.append(Issue(
            Issue.INFO, "Artifacts",
            f"{lone_escapes} lone escape characters found.",
        ))

    lone_numbers = sum(1 for l in lines if re.match(r'^\d{1,2}\.\s*$', l.strip()))
    if lone_numbers > 5:
        issues.append(Issue(
            Issue.WARNING, "Orphaned Numbers",
            f"{lone_numbers} bare numbered list items with no content. Text may have been lost.",
        ))

    bare_sub_items = sum(1 for l in lines if re.match(r'^-\s+[a-z]\.\s*$', l.strip()))
    if bare_sub_items > 3:
        issues.append(Issue(
            Issue.WARNING, "Orphaned Sub-items",
            f"{bare_sub_items} bare sub-list items (e.g. '- a.') with no content.",
        ))

    # --- Excessive blank lines ---
    max_consecutive_blank = 0
    current_blank = 0
    for line in lines:
        if line.strip() == '':
            current_blank += 1
            max_consecutive_blank = max(max_consecutive_blank, current_blank)
        else:
            current_blank = 0
    if max_consecutive_blank > 3:
        issues.append(Issue(
            Issue.INFO, "Blank Lines",
            f"Max {max_consecutive_blank} consecutive blank lines. Post-processor may need to run.",
        ))

    # --- Truncated sentences ---
    truncated = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (len(stripped) > 20 and
            not stripped.startswith('#') and
            not stripped.startswith('!') and
            not stripped.startswith('|') and
            not stripped.startswith('-') and
            not stripped.startswith('>') and
            not stripped.startswith('```') and
            not stripped.endswith('.') and
            not stripped.endswith(':') and
            not stripped.endswith(')') and
            not stripped.endswith('"') and
            not stripped.endswith("'") and
            not stripped.endswith('!') and
            not stripped.endswith('?') and
            not stripped.endswith(',') and
            stripped[0].islower()):
            truncated.append((i+1, stripped))
    # Only flag if there are many (some is normal for lists)
    if len(truncated) > 10:
        issues.append(Issue(
            Issue.INFO, "Possible Fragments",
            f"{len(truncated)} lines start with lowercase and don't end with punctuation. "
            "May indicate sentence fragments from broken extraction.",
            sample=truncated[0][1] if truncated else None
        ))

    # --- Summary ---
    critical = sum(1 for i in issues if i.severity == Issue.CRITICAL)
    warnings = sum(1 for i in issues if i.severity == Issue.WARNING)
    infos = sum(1 for i in issues if i.severity == Issue.INFO)

    if critical > 0:
        verdict = "NEEDS ATTENTION"
    elif warnings > 2:
        verdict = "REVIEW RECOMMENDED"
    elif warnings > 0:
        verdict = "MINOR ISSUES"
    else:
        verdict = "GOOD"

    return {
        'file': md_path.name,
        'verdict': verdict,
        'words': word_count,
        'lines': line_count,
        'headings': len(headings),
        'images': len(img_refs),
        'issues': issues,
        'critical': critical,
        'warnings': warnings,
        'infos': infos,
    }


def format_report(result: dict) -> str:
    """Format a verification result as a readable report."""
    lines = []
    icon = {"GOOD": "OK", "MINOR ISSUES": "~~", "REVIEW RECOMMENDED": "!!", "NEEDS ATTENTION": "XX"}
    lines.append(f"[{icon.get(result['verdict'], '??')}] {result['file']} — {result['verdict']}")
    lines.append(f"     {result['words']} words | {result['lines']} lines | {result['headings']} headings | {result['images']} images")
    if result['issues']:
        for issue in result['issues']:
            lines.append(str(issue))
    lines.append('')
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verify PDF-to-markdown conversion quality')
    parser.add_argument('path', help='Markdown file or directory (with --batch)')
    parser.add_argument('--batch', action='store_true', help='Verify all .md files in directory')
    parser.add_argument('--reference-dir', help='Directory containing original PDFs for size comparison')
    args = parser.parse_args()

    target = Path(args.path)
    ref_dir = Path(args.reference_dir) if args.reference_dir else None

    if args.batch:
        if not target.is_dir():
            print(f"Error: {target} is not a directory")
            exit(1)
        md_files = sorted(target.glob('*.md'))
        results = []
        for md_file in md_files:
            pdf_path = None
            if ref_dir:
                pdf_name = md_file.stem + '.pdf'
                pdf_path = ref_dir / pdf_name
            result = verify(md_file, pdf_path)
            results.append(result)
            print(format_report(result))

        # Summary
        total = len(results)
        good = sum(1 for r in results if r['verdict'] == 'GOOD')
        minor = sum(1 for r in results if r['verdict'] == 'MINOR ISSUES')
        review = sum(1 for r in results if r['verdict'] == 'REVIEW RECOMMENDED')
        attention = sum(1 for r in results if r['verdict'] == 'NEEDS ATTENTION')
        print(f"--- Summary: {total} files ---")
        print(f"  GOOD: {good} | MINOR: {minor} | REVIEW: {review} | NEEDS ATTENTION: {attention}")
    else:
        if not target.is_file():
            print(f"Error: {target} is not a file")
            exit(1)
        pdf_path = None
        if ref_dir:
            pdf_name = target.stem + '.pdf'
            pdf_path = ref_dir / pdf_name
        result = verify(target, pdf_path)
        print(format_report(result))
