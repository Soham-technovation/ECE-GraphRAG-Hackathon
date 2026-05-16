from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Dict, List, Tuple

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(
    documents: List[Dict],
    chunk_size: int = 500,
    chunk_overlap: int = 100,
) -> Tuple[List[Dict], Dict]:
    """Chunk documents into overlap windows and return chunk statistics."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    chunks: List[Dict] = []
    per_dataset: Counter = Counter()
    lengths: List[int] = []

    for doc_idx, doc in enumerate(documents):
        text = doc.get("text", "")
        parts = splitter.split_text(text)

        for chunk_idx, part in enumerate(parts):
            chunk_id = f"{doc_idx}_{chunk_idx}"
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": part,
                    "source": doc.get("source_path", ""),
                    "dataset": doc.get("dataset_name", "unknown"),
                    "filename": doc.get("filename", ""),
                }
            )
            per_dataset[doc.get("dataset_name", "unknown")] += 1
            lengths.append(len(part))

    stats = {
        "total_chunks": len(chunks),
        "avg_chunk_chars": mean(lengths) if lengths else 0,
        "min_chunk_chars": min(lengths) if lengths else 0,
        "max_chunk_chars": max(lengths) if lengths else 0,
        "chunks_per_dataset": dict(per_dataset),
    }
    return chunks, stats
