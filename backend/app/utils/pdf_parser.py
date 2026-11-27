"""PDF text extraction, Supreme Court metadata parsing, and verbatim passage chunking."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
from typing import List, Optional

import pymupdf


_MONTH_NAMES = (
    "january|february|march|april|may|june|july|august|september|october|november|december"
)
_DATE_RE = re.compile(
    rf"\b(?:\d{{1,2}}\s+(?:{_MONTH_NAMES})\s+\d{{4}}|(?:{_MONTH_NAMES})\s+\d{{1,2}},\s*\d{{4}})\b",
    re.IGNORECASE,
)
_CASE_NUM_RE = re.compile(
    r"\(((?:Civil|Criminal|Writ|Special Leave|Review|Curative|Transfer|Transferred|Election|Arbitration|Contempt|Tax)[^()\n]{3,110})\)",
    re.IGNORECASE,
)
_SCR_CITATION_RE = re.compile(
    r"(?:\[\d{4}\]|\(\d{4}\))\s+\d+(?:\s*\([^)]+\))?\s+S\.C\.R\.[^\n]*",
    re.IGNORECASE,
)
_MARGIN_NOISE_RE = re.compile(r"^[A-H•j\)\(\d\s.,;:\-]+$")


@dataclass(frozen=True)
class ParsedJudgmentDocument:
    """Extracted document metadata and full verbatim text for one judgment PDF."""

    doc_id: str
    relative_path: str
    category: str
    court: str
    title: str
    citation: str
    date: str
    context: str
    full_text: str


@dataclass(frozen=True)
class PassageChunk:
    """Verbatim passage slice from a ParsedJudgmentDocument with exact offsets."""

    chunk_id: int
    doc_id: str
    category: str
    court: str
    title: str
    citation: str
    date: str
    context: str
    offset_start: int
    offset_end: int
    excerpt: str


def _parse_iso_date(header_text: str) -> str:
    match = _DATE_RE.search(header_text)
    if not match:
        return ""
    raw = re.sub(r"\s+", " ", match.group(0)).replace(",", ", ").strip()
    raw = re.sub(r",\s+", ", ", raw)
    for fmt in ("%d %B %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(raw.title(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return ""


def _clean_header_lines(raw_text: str, max_lines: int = 45) -> List[str]:
    lines: List[str] = []
    for line in raw_text.splitlines()[:80]:
        stripped = " ".join(line.split()).strip()
        if not stripped:
            continue
        if stripped.upper() == "CASE DETAILS":
            continue
        if len(stripped) <= 2 and _MARGIN_NOISE_RE.match(stripped):
            continue
        lines.append(stripped)
        if len(lines) >= max_lines:
            break
    return lines


def _extract_title(lines: List[str], fallback_name: str) -> str:
    for idx, line in enumerate(lines[:25]):
        if re.fullmatch(r"v\.?|vs\.?", line, flags=re.IGNORECASE):
            left_parts: List[str] = []
            for j in range(idx - 1, -1, -1):
                cand = lines[j]
                if _SCR_CITATION_RE.search(cand) or cand.isdigit():
                    break
                left_parts.insert(0, cand)
                if len(left_parts) >= 2:
                    break

            right_parts: List[str] = []
            for j in range(idx + 1, min(len(lines), idx + 5)):
                cand = lines[j]
                if (
                    cand.startswith("(")
                    or cand.startswith("[")
                    or _DATE_RE.search(cand)
                    or _SCR_CITATION_RE.search(cand)
                ):
                    break
                right_parts.append(cand)
                if len(right_parts) >= 2:
                    break

            if left_parts and right_parts:
                return f"{' '.join(left_parts)} v. {' '.join(right_parts)}"

        inline_match = re.search(r"^(.{2,100}?)\s+(?:v\.|vs\.?)\s+(.{2,100})$", line, re.IGNORECASE)
        if inline_match and not _SCR_CITATION_RE.search(line):
            return f"{inline_match.group(1).strip()} v. {inline_match.group(2).strip()}"

    return fallback_name


def _extract_citation(header_text: str, fallback: str) -> str:
    case_match = _CASE_NUM_RE.search(header_text)
    if case_match:
        return " ".join(case_match.group(1).split())
    scr_match = _SCR_CITATION_RE.search(header_text)
    if scr_match:
        return " ".join(scr_match.group(0).split())
    return fallback


def parse_judgment_pdf(pdf_path: Path, dataset_root: Path) -> ParsedJudgmentDocument:
    """Extract verbatim text and structured Supreme Court metadata from a PDF."""
    rel_path = pdf_path.relative_to(dataset_root).as_posix()
    category = pdf_path.parent.name
    doc_id = rel_path

    doc = pymupdf.open(pdf_path)
    try:
        full_text = "\n".join(page.get_text("text") for page in doc)
    finally:
        doc.close()

    header_slice = full_text[:3500]
    header_lines = _clean_header_lines(header_slice)

    title = _extract_title(header_lines, fallback_name=pdf_path.stem)
    citation = _extract_citation(header_slice, fallback=pdf_path.stem)
    date = _parse_iso_date(header_slice)

    return ParsedJudgmentDocument(
        doc_id=doc_id,
        relative_path=rel_path,
        category=category,
        court="SUPREME COURT OF INDIA",
        title=title,
        citation=citation,
        date=date,
        context=f"Precedent on {category}.",
        full_text=full_text,
    )


def chunk_judgment_document(
    document: ParsedJudgmentDocument,
    start_chunk_id: int,
    chunk_size: int = 2400,
    overlap: int = 350,
    min_chunk_chars: int = 450,
) -> List[PassageChunk]:
    """Split judgment text into overlapping verbatim chunks with exact character offsets."""
    text = document.full_text
    text_len = len(text)
    if text_len == 0:
        return []

    chunks: List[PassageChunk] = []
    pos = 0
    chunk_id = start_chunk_id

    while pos < text_len:
        target_end = min(pos + chunk_size, text_len)
        if target_end < text_len:
            # Snap cleanly to a sentence or whitespace boundary near target_end
            window_start = max(pos + int(chunk_size * 0.72), pos + 1)
            snap_period = text.rfind(". ", window_start, target_end)
            snap_newline = text.rfind("\n", window_start, target_end)
            snap_space = text.rfind(" ", window_start, target_end)
            if snap_period != -1:
                target_end = snap_period + 1
            elif snap_newline != -1:
                target_end = snap_newline
            elif snap_space != -1:
                target_end = snap_space

        raw_slice = text[pos:target_end]
        left_trim = len(raw_slice) - len(raw_slice.lstrip())
        right_trim = len(raw_slice) - len(raw_slice.rstrip())
        adj_start = pos + left_trim
        adj_end = target_end - right_trim

        if adj_end > adj_start:
            excerpt = text[adj_start:adj_end]
            if len(excerpt) >= min_chunk_chars or len(chunks) == 0:
                chunks.append(
                    PassageChunk(
                        chunk_id=chunk_id,
                        doc_id=document.doc_id,
                        category=document.category,
                        court=document.court,
                        title=document.title,
                        citation=document.citation,
                        date=document.date,
                        context=document.context,
                        offset_start=adj_start,
                        offset_end=adj_end,
                        excerpt=excerpt,
                    )
                )
                chunk_id += 1

        if target_end >= text_len:
            break

        next_pos = target_end - overlap
        pos = next_pos if next_pos > pos else target_end

    return chunks
