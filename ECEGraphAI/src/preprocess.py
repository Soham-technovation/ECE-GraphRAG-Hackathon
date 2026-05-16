from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _remove_strange_symbols(text: str) -> str:
    # Preserve common math symbols and equations while removing noisy glyphs.
    return re.sub(r"[^\w\s\.,;:\-\+\=\(\)\[\]\{\}/\\\*\^%<>|~`$#@!?&'\"\n]", " ", text)


def _remove_repeated_headers_footers(text: str, repeated_lines: set[str]) -> str:
    lines = [ln.rstrip() for ln in text.splitlines()]
    filtered = [ln for ln in lines if ln.strip() not in repeated_lines]
    return "\n".join(filtered)


def _detect_repeated_header_footer_lines(docs: List[Dict], top_n: int = 2) -> set[str]:
    candidates: Counter = Counter()
    for doc in docs:
        lines = [ln.strip() for ln in doc.get("text", "").splitlines() if ln.strip()]
        if not lines:
            continue
        for ln in lines[:top_n] + lines[-top_n:]:
            if len(ln) > 3:
                candidates[ln] += 1

    # Treat line as repeated template if it appears in at least 3 documents.
    return {line for line, count in candidates.items() if count >= 3}


def clean_text(text: str, lowercase: bool = False, repeated_lines: set[str] | None = None) -> str:
    """Clean text while preserving equations and technical notation."""
    value = text or ""

    if repeated_lines:
        value = _remove_repeated_headers_footers(value, repeated_lines)

    value = _remove_strange_symbols(value)
    value = _normalize_whitespace(value)

    if lowercase:
        # Lowercasing is optional because variable names/equations can be case sensitive.
        value = value.lower()

    return value


def preprocess_documents(documents: List[Dict], lowercase: bool = False) -> List[Dict]:
    """Preprocess docs and remove duplicate contents across datasets."""
    repeated_lines = _detect_repeated_header_footer_lines(documents)

    seen_texts: set[str] = set()
    cleaned_docs: List[Dict] = []

    for doc in documents:
        cleaned = clean_text(doc.get("text", ""), lowercase=lowercase, repeated_lines=repeated_lines)
        if not cleaned:
            continue
        if cleaned in seen_texts:
            continue

        seen_texts.add(cleaned)
        item = dict(doc)
        item["text"] = cleaned
        cleaned_docs.append(item)

    return cleaned_docs
