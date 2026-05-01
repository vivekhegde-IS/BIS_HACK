#!/usr/bin/env python3
"""
Component 1: Ingest (PERSON A)
Extract Indian Standards from BIS_SP_21.pdf and save as chunks.json

Usage:
    python src/ingest.py

Output: chunks.json
"""

import json
import re
import os
import sys
from dotenv import load_dotenv

load_dotenv()

PDF_PATH = os.getenv('PDF_PATH', './data/BIS_SP_21.pdf')
CHUNKS_PATH = os.getenv('CHUNKS_PATH', './chunks.json')


def extract_text_from_pdf(pdf_path):
    """Extract full text from PDF. Tries pdftotext first, then PyMuPDF."""
    try:
        import pdftotext
        with open(pdf_path, 'rb') as f:
            pdf = pdftotext.PDF(f)
        text = '\n'.join(pdf)
        print(f"  [pdftotext] Extracted {len(text)} characters from {len(pdf)} pages")
        return text
    except ImportError:
        print("  pdftotext not available, trying PyMuPDF (fitz)...")
    except Exception as e:
        print(f"  pdftotext error: {e}, trying PyMuPDF...")

    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        text = ''
        for page in doc:
            text += page.get_text()
        print(f"  [PyMuPDF] Extracted {len(text)} characters from {doc.page_count} pages")
        return text
    except ImportError:
        raise ImportError(
            "No PDF library available. Install one:\n"
            "  pip install pdftotext  (requires poppler)\n"
            "  pip install PyMuPDF    (pure Python fallback)"
        )


# IS code pattern: IS 269 : 1989, IS 2185 (Part 2) : 1983, IS 1489 (Part 1) : 1991
IS_PATTERN = re.compile(
    r'\bIS\s+\d+(?:\s*\(Part\s*\d+\))?(?:\s*\(Section\s*\d+\))?\s*:\s*\d{4}\b',
    re.IGNORECASE
)


def normalize_is_code(raw):
    """Normalize IS code string: 'IS 269 : 1989' → 'IS 269: 1989'"""
    raw = re.sub(r'\s*:\s*', ': ', raw.strip())
    raw = re.sub(r'\s+', ' ', raw)
    return raw


def parse_is_standards(text):
    """
    Parse IS standard entries from extracted PDF text.
    Returns list of chunk dicts: {id, standard, text, description}
    """
    chunks = []
    seen_codes = set()

    # Find all IS code positions
    matches = list(IS_PATTERN.finditer(text))

    if not matches:
        print("  WARNING: No IS codes found with primary pattern. Trying relaxed pattern...")
        # Relaxed: IS followed by digits somewhere
        relaxed = re.compile(r'\bIS[\s\-]+\d{2,6}', re.IGNORECASE)
        matches = list(relaxed.finditer(text))

    print(f"  Found {len(matches)} IS code occurrences in PDF text")

    for i, match in enumerate(matches):
        is_code_raw = match.group(0)
        is_code = normalize_is_code(is_code_raw)

        # Skip duplicates — keep first occurrence (most detailed)
        if is_code in seen_codes:
            continue
        seen_codes.add(is_code)

        # Extract surrounding context (up to next IS code or 1500 chars)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else min(start + 1500, len(text))
        section_text = text[start:end].strip()

        # Get description: everything after the IS code on the same/next line
        after_code = section_text[len(is_code_raw):].strip()
        # First 300 chars as description
        description = re.sub(r'\s+', ' ', after_code[:300]).strip()

        # Full text for TF-IDF indexing
        full_text = f"{is_code} {section_text[:1500]}"
        full_text = re.sub(r'\s+', ' ', full_text).strip()

        chunk = {
            "id": is_code,
            "standard": is_code,
            "text": full_text,
            "description": description
        }
        chunks.append(chunk)

    return chunks


def main():
    """Main ingestion pipeline."""
    pdf_path = PDF_PATH

    if not os.path.exists(pdf_path):
        print(f"ERROR: PDF not found at '{pdf_path}'")
        print("Place BIS_SP_21.pdf inside the data/ folder and retry.")
        sys.exit(1)

    print(f"Step 1: Extracting text from {pdf_path} ...")
    text = extract_text_from_pdf(pdf_path)

    print("Step 2: Parsing IS standards ...")
    chunks = parse_is_standards(text)

    if not chunks:
        print("ERROR: No IS standards extracted. Check PDF content/format.")
        sys.exit(1)

    print(f"Step 3: Saving {len(chunks)} chunks to {CHUNKS_PATH} ...")
    with open(CHUNKS_PATH, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {len(chunks)} IS standards saved to {CHUNKS_PATH}")
    print("Preview (first 5):")
    for chunk in chunks[:5]:
        print(f"  {chunk['standard']:30s} | {chunk['description'][:60]}...")


if __name__ == "__main__":
    main()
