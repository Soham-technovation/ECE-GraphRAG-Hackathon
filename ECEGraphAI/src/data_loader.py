from __future__ import annotations

import json
import logging
from collections import Counter
from pathlib import Path
from typing import Dict, List

import pandas as pd
from bs4 import BeautifulSoup

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".json", ".html", ".htm", ".csv"}


def configure_logger(log_file: Path | None = None) -> logging.Logger:
    logger = logging.getLogger("ecegraphai.data_loader")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def _read_pdf(path: Path) -> str:
    text_parts: List[str] = []

    if pdfplumber is not None:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    text_parts.append(page_text)
    elif PdfReader is not None:
        reader = PdfReader(str(path))
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text:
                text_parts.append(page_text)
    else:
        raise ImportError("Install `pdfplumber` or `PyPDF2` to read PDF files.")

    return "\n".join(text_parts)


def _read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _read_json(path: Path) -> str:
    payload = json.loads(path.read_text(encoding="utf-8", errors="ignore"))

    if isinstance(payload, dict):
        return json.dumps(payload, ensure_ascii=True)
    if isinstance(payload, list):
        return "\n".join(json.dumps(item, ensure_ascii=True) for item in payload)
    return str(payload)


def _read_html(path: Path) -> str:
    content = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def _read_csv(path: Path) -> str:
    frame = pd.read_csv(path)
    return frame.fillna("").astype(str).agg(" ".join, axis=1).str.cat(sep="\n")


def _load_single_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _read_pdf(path)
    if suffix == ".txt":
        return _read_txt(path)
    if suffix == ".json":
        return _read_json(path)
    if suffix in {".html", ".htm"}:
        return _read_html(path)
    if suffix == ".csv":
        return _read_csv(path)
    raise ValueError(f"Unsupported file extension: {suffix}")


def load_documents(data_dir: str | Path, log_file: str | Path | None = None) -> List[Dict]:
    """Recursively scan data folders and load documents.

    Returns list of document dicts with:
    - text
    - source_path
    - filename
    - dataset_name
    """
    data_root = Path(data_dir)
    logger = configure_logger(Path(log_file) if log_file else None)

    if not data_root.exists():
        raise FileNotFoundError(f"Data directory not found: {data_root}")

    documents: List[Dict] = []
    ext_counts: Counter = Counter()
    dataset_counts: Counter = Counter()
    error_count = 0

    for file_path in data_root.rglob("*"):
        if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        dataset_name = file_path.relative_to(data_root).parts[0] if file_path.relative_to(data_root).parts else "unknown"

        try:
            text = _load_single_file(file_path).strip()
            if not text:
                logger.warning("Skipping empty document: %s", file_path)
                continue

            documents.append(
                {
                    "text": text,
                    "source_path": str(file_path),
                    "filename": file_path.name,
                    "dataset_name": dataset_name,
                }
            )
            ext_counts[file_path.suffix.lower()] += 1
            dataset_counts[dataset_name] += 1
        except Exception as exc:
            error_count += 1
            logger.exception("Failed loading %s: %s", file_path, exc)

    logger.info("Loaded %d documents from %s", len(documents), data_root)
    logger.info("File-type stats: %s", dict(ext_counts))
    logger.info("Dataset stats: %s", dict(dataset_counts))
    logger.info("Failed documents: %d", error_count)

    return documents
