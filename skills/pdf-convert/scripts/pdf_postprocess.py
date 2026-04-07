"""
Post-process Docling PDF-to-markdown conversions.

Fixes common issues:
- Reorganizes extracted images into a flat images/ folder
- Fixes image references in markdown to use relative paths
- Decodes HTML entities (&amp; -> &, etc.)
- Removes stray artifacts (lone periods, trailing whitespace)
- Strips line numbers that bleed through from academic papers

Usage:
    python tools/pdf_postprocess.py <md_file> [--images-dir images]
    python tools/pdf_postprocess.py --batch <directory> [--images-dir images]
"""

import argparse
import html
import os
import re
import shutil
from pathlib import Path


def fix_image_references(content: str, md_path: Path, images_dir: Path) -> str:
    """Move referenced images to images_dir and fix markdown references."""
    md_dir = md_path.parent

    def replace_image(match):
        alt = match.group(1)
        img_path_str = match.group(2)
        img_path = md_dir / img_path_str

        if not img_path.exists():
            abs_attempt = Path(img_path_str)
            if abs_attempt.exists():
                img_path = abs_attempt

        if img_path.exists():
            images_dir.mkdir(parents=True, exist_ok=True)
            new_name = img_path.name
            # Shorten hash-based filenames
            name_match = re.match(r'(image_\d+)_[a-f0-9]+(\.\w+)', new_name)
            if name_match:
                stem = md_path.stem.replace(' ', '_')[:40]
                new_name = f"{stem}_{name_match.group(1)}{name_match.group(2)}"

            dest = images_dir / new_name
            if not dest.exists():
                shutil.copy2(img_path, dest)

            rel_path = os.path.relpath(dest, md_dir)
            return f"![{alt}]({rel_path})"
        else:
            return match.group(0)

    pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
    return re.sub(pattern, replace_image, content)


def decode_html_entities(content: str) -> str:
    """Decode HTML entities like &amp; -> &."""
    return html.unescape(content)


STRUCTURAL_HEADINGS = {
    'abstract', 'introduction', 'conclusion', 'conclusions', 'references',
    'bibliography', 'acknowledgements', 'acknowledgments', 'foreword',
    'preface', 'table of contents', 'contents', 'executive summary',
    'glossary', 'appendix', 'methodology', 'methods', 'results',
    'discussion', 'about the authors', 'disclaimer',
}

SECTION_NUMBER_RE = re.compile(
    r'^(\d+(?:\.\d+)*)\.?\s+'
)

CHAPTER_RE = re.compile(
    r'^(CHAPTER|Chapter|PART|Part)\s+(\d+|[IVXLC]+)\b', re.IGNORECASE
)


def fix_heading_hierarchy(content: str) -> str:
    """
    Rebuild heading hierarchy from flat ## headings that Docling produces.

    Strategy:
    1. First heading in the document → H1 (document title)
    2. CHAPTER/PART headings → H2
    3. Structural headings (Introduction, Conclusion, etc.) → H2
    4. Numbered sections: depth from number (1 → H2, 1.1 → H3, 1.1.1 → H4)
    5. ALL CAPS headings → H2 (major sections)
    6. Demote false headings: sentences ending in period, very long text,
       quotes — convert to bold paragraph
    7. Remaining headings → H3 (subsections under the nearest structural heading)
    """
    lines = content.split('\n')
    result = []
    found_title = False

    for i, line in enumerate(lines):
        heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
        if not heading_match:
            result.append(line)
            continue

        text = heading_match.group(2).strip()

        # Skip empty or garbage headings (glyph IDs, etc.)
        if not text or re.match(r'^[/\\]gid\d', text):
            result.append(line)
            continue

        # Demote bullet markers and list items incorrectly parsed as headings
        if re.match(r'^[\·\•\-\*]\s*$', text) or re.match(r'^\d{1,2}\.?\s*$', text):
            if text.strip() in ('·', '•', '-', '*', ''):
                continue  # Drop entirely
            result.append(text)  # Keep as plain text
            continue

        new_level = _determine_heading_level(text, found_title)

        if new_level == 0:
            # Demote to bold paragraph (false heading)
            result.append(f'**{text}**')
            continue

        if new_level == 1:
            if found_title:
                new_level = 2
            else:
                found_title = True

        prefix = '#' * new_level
        result.append(f'{prefix} {text}')

    return '\n'.join(result)


def _determine_heading_level(text: str, title_assigned: bool) -> int:
    """
    Determine the correct heading level for a given heading text.
    Returns 0 to demote to non-heading (bold paragraph).
    """
    stripped = text.strip()
    lower = stripped.lower()

    # False heading detection: full sentences ending in period
    if stripped.endswith('.') and len(stripped) > 60:
        return 0

    # False heading: quotes (starts with ' or ")
    if stripped.startswith(("'", '"', '\u2018', '\u201C', "'", '"')):
        if len(stripped) > 40:
            return 0

    # False heading: very long text that reads like a paragraph
    if len(stripped) > 120 and ' ' in stripped:
        return 0

    # Document title: first heading in the document
    if not title_assigned:
        return 1

    # CHAPTER / PART headings → H2
    if CHAPTER_RE.match(stripped):
        return 2

    # Structural headings → H2
    # Clean any leading numbers for comparison
    text_no_num = SECTION_NUMBER_RE.sub('', lower).strip()
    if text_no_num in STRUCTURAL_HEADINGS:
        return 2

    # Numbered sections: determine depth from section number
    num_match = SECTION_NUMBER_RE.match(stripped)
    if num_match:
        num_str = num_match.group(1)
        depth = num_str.count('.') + 1
        # 1 → H2, 1.1 → H3, 1.1.1 → H4, cap at H5
        return min(depth + 1, 5)

    # ALL CAPS with reasonable length → H2
    alpha_chars = re.sub(r'[^a-zA-Z]', '', stripped)
    if alpha_chars and alpha_chars == alpha_chars.upper() and len(alpha_chars) >= 3:
        if len(stripped) <= 80:
            return 2

    # BOX, EXHIBIT, FIGURE labels → H4 (minor)
    if re.match(r'^(BOX|EXHIBIT|FIGURE|TABLE)\s+\d', stripped, re.IGNORECASE):
        return 4

    # Short heading without numbers → H3 (subsection)
    if len(stripped) <= 80:
        return 3

    # Longer headings that passed false-heading checks → H3
    return 3


def fix_glyph_ids(content: str) -> str:
    """Remove unresolved font glyph ID references (/gidXXXXX patterns)."""
    had_glyphs = '/gid' in content
    content = re.sub(r'/gid\d{5}', '', content)
    # Clean up headings that are now empty after glyph removal
    content = re.sub(r'^(#{1,6})\s*\n', '\n', content, flags=re.MULTILINE)
    # Clean up excessive spaces left behind
    content = re.sub(r'  +', ' ', content)

    if had_glyphs:
        content = _clean_glyph_aftermath(content)

    return content


def _clean_glyph_aftermath(content: str) -> str:
    """
    Clean artifacts left after stripping glyph IDs:
    lone escape chars, empty tables, bare quotes/dashes, orphaned numbers.
    """
    lines = content.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty table rows (all cells empty)
        if re.match(r'^\|[\s|]*\|$', stripped) and not re.search(r'[a-zA-Z0-9]', stripped):
            i += 1
            continue
        # Skip table separator rows that follow empty tables
        if re.match(r'^\|[-\s|]+\|$', stripped):
            # Check if previous non-blank line was also a table row
            prev_content = [r for r in result if r.strip()]
            if prev_content and re.match(r'^\|[\s|]*\|$', prev_content[-1].strip()):
                i += 1
                continue

        # Skip lone escape characters
        if stripped in ('\\_', '\\_\\_', '\\'):
            i += 1
            continue

        # Skip lone quote marks
        if stripped in ("'", '"', '\u2018', '\u2019', '\u201C', '\u201D'):
            i += 1
            continue

        # Skip lone dashes (not horizontal rules)
        if stripped == '-':
            i += 1
            continue

        # Skip bare list numbers with no content (e.g. "1." or "2." alone)
        if re.match(r'^\d+\.\s*$', stripped):
            i += 1
            continue

        # Skip duplicate consecutive identical lines
        if result and stripped and stripped == result[-1].strip():
            i += 1
            continue

        # Skip printer/binding instructions
        if any(phrase in stripped.lower() for phrase in [
            'spine of this book', 'please do not add',
            'too small to s spine', 'could cause the book to be rej'
        ]):
            i += 1
            continue

        result.append(line)
        i += 1

    return '\n'.join(result)


def fix_unicode_ligatures(content: str) -> str:
    """Fix unresolved Unicode ligature references from PDF extraction."""
    ligatures = {
        '/uniFB01': 'fi',
        '/uniFB02': 'fl',
        '/uniFB00': 'ff',
        '/uniFB03': 'ffi',
        '/uniFB04': 'ffl',
        '/uni00AD': '',  # soft hyphen
        '/uni2019': "'",
        '/uni2018': "'",
        '/uni201C': '"',
        '/uni201D': '"',
        '/uni2013': '–',
        '/uni2014': '—',
    }
    for code, replacement in ligatures.items():
        content = content.replace(code, replacement)
    # Generic pattern for remaining /uniXXXX references
    def replace_uni(match):
        try:
            return chr(int(match.group(1), 16))
        except (ValueError, OverflowError):
            return match.group(0)
    content = re.sub(r'/uni([0-9A-Fa-f]{4})', replace_uni, content)
    return content


def fix_spaced_ligatures(content: str) -> str:
    """
    Fix ligatures that Docling renders as space-separated characters.
    Common in Frontiers/Springer papers: 'fi nance' → 'finance', 'ef fi cacy' → 'efficacy'.

    Patterns seen:
    - ' fi ' mid-word: "ef fi cacy" → "efficacy"
    - ' fl ' mid-word: "con fl ict" → "conflict"
    - ' fi' at word start: "fi nance" → "finance" (space before, joins with next)
    """
    # Mid-word: letter + space + ligature + space + letter → rejoin
    content = re.sub(r'(?<=[a-zA-Z]) fi (?=[a-z])', 'fi', content)
    content = re.sub(r'(?<=[a-zA-Z]) fl (?=[a-z])', 'fl', content)
    content = re.sub(r'(?<=[a-zA-Z]) ff (?=[a-z])', 'ff', content)
    content = re.sub(r'(?<=[a-zA-Z]) ffi (?=[a-z])', 'ffi', content)
    content = re.sub(r'(?<=[a-zA-Z]) ffl (?=[a-z])', 'ffl', content)

    # Word-start: space/start + ligature + space + letter → rejoin
    # e.g. "realm of fi nance" → "realm of finance"
    content = re.sub(r'(?<=\s)fi (?=[a-z])', 'fi', content)
    content = re.sub(r'(?<=\s)fl (?=[a-z])', 'fl', content)

    return content


def strip_watermarks(content: str) -> str:
    """Remove repeated watermark/confidentiality text embedded in PDFs."""
    watermark_patterns = [
        r'Confidential\s+Do\s+Not\s+Share\s*',
        r'everdred\s*',  # no word boundary — often concatenated mid-word
    ]
    for pat in watermark_patterns:
        content = re.sub(pat, '', content, flags=re.IGNORECASE)
    # Clean up lines that are now empty after watermark removal
    content = re.sub(r'^\s+$', '', content, flags=re.MULTILINE)
    return content


def strip_cc_icon_fragments(content: str) -> str:
    """
    Remove Creative Commons icon text fragments that OCR picks up from
    license badge images (e.g. lone 'C', 'CI', 'BY', 'NC', 'SA', 'VI').
    Only strips when they appear as isolated short lines near other fragments.
    """
    cc_tokens = {'C', 'CI', 'BY', 'NC', 'SA', 'ND', 'VI'}
    lines = content.split('\n')
    result = []
    i = 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped in cc_tokens:
            # Check if neighboring lines are also CC tokens or blank
            prev_is_cc_or_blank = (not result or result[-1].strip() in cc_tokens or result[-1].strip() == '')
            next_stripped = lines[i+1].strip() if i+1 < len(lines) else ''
            next_is_cc_or_blank = (next_stripped in cc_tokens or next_stripped == '' or next_stripped.startswith('!['))
            if prev_is_cc_or_blank and next_is_cc_or_blank:
                i += 1
                continue
        result.append(lines[i])
        i += 1
    return '\n'.join(result)


def fix_duplicate_lines(content: str) -> str:
    """
    Remove lines that are exact duplicates of the previous non-blank line,
    common in two-column academic paper end-matter where both columns
    have identical text.
    """
    lines = content.split('\n')
    result = []
    last_content = ''
    for line in lines:
        stripped = line.strip()
        if stripped and stripped == last_content and len(stripped) > 30:
            continue
        result.append(line)
        if stripped:
            last_content = stripped
    return '\n'.join(result)


def fix_hyphenation_artifacts(content: str) -> str:
    """Fix words split by hyphenation at PDF column/page breaks."""
    # Pattern: word fragment ending with hyphen at end of line, continuation on next line
    # e.g. "defini-\ntions" → "definitions"
    content = re.sub(r'(\w+)-\n(\w+)', r'\1\2', content)
    # Also fix mid-line hyphenation: "defini-tions" → "definitions"
    # Only for known common patterns to avoid false positives
    content = re.sub(r'(?<=[a-z])- (?=[a-z])', '', content)
    return content


def remove_stray_artifacts(content: str) -> str:
    """Remove common conversion artifacts."""
    # Remove lone periods on their own line (page break artifacts)
    content = re.sub(r'\n\.\n', '\n\n', content)
    # Remove trailing whitespace on lines
    content = re.sub(r' +\n', '\n', content)
    # Remove publisher metadata artifacts (e.g. "1234567890():,;")
    content = re.sub(r'^1234567890\(\):,;\s*\n', '', content)
    # Collapse 3+ consecutive blank lines to 2
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content


def fix_academic_line_numbers(content: str) -> str:
    """
    Remove line numbers that bleed through from academic paper formats.
    Matches patterns like table cells containing just numbers (1, 2, 3...)
    that appear in the left column of incorrectly parsed academic layouts.
    """
    # Pattern: table rows where first cell is just a line number
    # e.g. "| 38    |" as a standalone meaningless row
    lines = content.split('\n')
    cleaned = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Standalone line numbers (e.g. "38\n\n39\n\n40")
        if re.match(r'^\d{1,3}$', line.strip()) and len(line.strip()) <= 3:
            # Check if surrounded by blank lines (isolated number)
            prev_blank = (i == 0 or lines[i-1].strip() == '')
            next_blank = (i == len(lines) - 1 or lines[i+1].strip() == '')
            if prev_blank and next_blank:
                i += 1
                continue
        cleaned.append(line)
        i += 1
    return '\n'.join(cleaned)


def fix_broken_table_format(content: str) -> str:
    """
    Fix tables where academic paper content got parsed into table format
    incorrectly. Handles two patterns:

    1. Line-numbered tables: first column is sequential numbers, content in remaining columns
    2. Duplicated two-column tables: both columns contain identical text (from two-column PDF layouts)
    """
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        if lines[i].startswith('|') and '|' in lines[i][1:]:
            # Collect the full table block
            table_start = i
            table_lines = []
            while i < len(lines) and lines[i].startswith('|'):
                table_lines.append(lines[i])
                i += 1

            extracted = _extract_from_broken_table(table_lines)
            if extracted is not None:
                result.extend(extracted)
                result.append('')
            else:
                result.extend(table_lines)
            continue

        result.append(lines[i])
        i += 1

    return '\n'.join(result)


def _extract_from_broken_table(table_lines: list) -> list:
    """
    Attempt to extract clean text from a broken table.
    Returns list of clean text lines, or None if the table looks legitimate.
    """
    content_rows = []
    separator_count = 0

    for line in table_lines:
        if re.match(r'^\|[-\s|]+\|$', line):
            separator_count += 1
            continue
        cells = [c.strip() for c in line.split('|')]
        cells = [c for c in cells if c != '']
        content_rows.append(cells)

    if not content_rows:
        return None

    # Pattern 1: Line-numbered table (first cell is numbers)
    # Allow for some rows to have empty first cells (continuation rows)
    numbered_count = sum(
        1 for cells in content_rows
        if cells and len(cells) >= 2 and re.match(r'^\d+(\s+\d+)*$', cells[0])
    )
    if numbered_count > len(content_rows) * 0.5:
        extracted = []
        for cells in content_rows:
            if len(cells) >= 2:
                # Skip the line number column, join remaining
                if re.match(r'^\d+(\s+\d+)*$', cells[0]):
                    text = ' '.join(cells[1:])
                else:
                    text = ' '.join(cells)
            else:
                text = ' '.join(cells)
            if text.strip():
                extracted.append(text.strip())
        if extracted:
            return extracted

    # Pattern 2: Duplicated columns (two-column PDF layout parsed as table)
    # Both columns contain the same or nearly same text
    duplicated = True
    has_enough_rows = len(content_rows) >= 2
    for cells in content_rows:
        if len(cells) == 2:
            # Check if both cells are identical or nearly identical
            if cells[0] != cells[1]:
                # Allow for minor differences (whitespace, etc)
                if cells[0].replace(' ', '') != cells[1].replace(' ', ''):
                    # Check if one is a section number and other is content
                    if not (re.match(r'^\d+(\.\d+)*$', cells[0]) and len(cells[1]) > 10):
                        duplicated = False
                        break
        elif len(cells) == 1:
            continue
        else:
            duplicated = False
            break

    if duplicated and has_enough_rows:
        extracted = []
        for cells in content_rows:
            if len(cells) == 2:
                if re.match(r'^\d+(\.\d+)*$', cells[0]) and len(cells[1]) > 10:
                    # Section number + title
                    extracted.append(f"## {cells[0]} {cells[1]}")
                else:
                    # Take the first (or longer) cell
                    text = cells[0] if len(cells[0]) >= len(cells[1]) else cells[1]
                    if text.strip():
                        extracted.append(text.strip())
                        extracted.append('')
            elif len(cells) == 1 and cells[0].strip():
                extracted.append(cells[0].strip())
        if extracted:
            return extracted

    return None


def cleanup_artifacts_dirs(md_dir: Path):
    """Remove empty artifact directories left by Docling."""
    for item in md_dir.rglob('*_artifacts'):
        if item.is_dir():
            shutil.rmtree(item, ignore_errors=True)
    # Clean up nested path directories Docling creates
    nested = md_dir / 'projects'
    if nested.exists():
        shutil.rmtree(nested, ignore_errors=True)


def postprocess(md_path: Path, images_dir: Path = None):
    """Run all post-processing steps on a converted markdown file."""
    if images_dir is None:
        images_dir = md_path.parent / 'images'

    content = md_path.read_text(encoding='utf-8')
    original_size = len(content)

    content = fix_image_references(content, md_path, images_dir)
    content = decode_html_entities(content)
    content = fix_unicode_ligatures(content)
    content = fix_spaced_ligatures(content)
    content = fix_glyph_ids(content)
    content = fix_academic_line_numbers(content)
    content = fix_broken_table_format(content)
    content = fix_heading_hierarchy(content)
    content = strip_watermarks(content)
    content = strip_cc_icon_fragments(content)
    content = fix_duplicate_lines(content)
    content = fix_hyphenation_artifacts(content)
    # Run artifact cleanup last — other fixes can introduce new blank lines
    content = remove_stray_artifacts(content)

    md_path.write_text(content, encoding='utf-8')

    new_size = len(content)
    cleanup_artifacts_dirs(md_path.parent)

    return {
        'file': md_path.name,
        'original_size': original_size,
        'cleaned_size': new_size,
        'reduction': f"{((original_size - new_size) / original_size * 100):.1f}%" if original_size > 0 else "0%"
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Post-process Docling conversions')
    parser.add_argument('path', help='Markdown file or directory (with --batch)')
    parser.add_argument('--batch', action='store_true', help='Process all .md files in directory')
    parser.add_argument('--images-dir', default='images', help='Images directory name (relative to md dir)')
    args = parser.parse_args()

    target = Path(args.path)

    if args.batch:
        if not target.is_dir():
            print(f"Error: {target} is not a directory")
            exit(1)
        md_files = sorted(target.glob('*.md'))
        images_dir = target / args.images_dir
        for md_file in md_files:
            result = postprocess(md_file, images_dir)
            print(f"  {result['file']}: {result['reduction']} reduction")
    else:
        if not target.is_file():
            print(f"Error: {target} is not a file")
            exit(1)
        images_dir = target.parent / args.images_dir
        result = postprocess(target, images_dir)
        print(f"  {result['file']}: {result['reduction']} reduction")
