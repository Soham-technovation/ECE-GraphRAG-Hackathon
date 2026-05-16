"""
organize_datasets.py

Scan project files and organize dataset files into data/ subfolders by keywords.

Usage:
    python organize_datasets.py --root .

Features:
- Recursively scans for .pdf, .txt, .json, .html, .csv files
- Classifies files using filename keywords and moves them into data/<category>/
- Creates destination folders if missing
- Avoids duplicates by adding numeric suffixes
- Logging, exception handling, progress messages, and summary statistics
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# File extensions to consider
EXTENSIONS = {".pdf", ".txt", ".json", ".html", ".csv"}


CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    "MIT_OCW": ["mit", "ocw", "lecture", "assignment", "electrical", "electronics"],
    "NPTEL": ["nptel", "transcript", "course", "ece"],
    "AllAboutCircuits": ["circuit", "amplifier", "resistor", "transistor", "bjt"],
    "OpenStax": ["openstax", "physics", "engineering"],
    "HotpotQA": ["hotpot"],
    "SQuAD": ["squad"],
    "NaturalQuestions": ["natural_questions", "nq"],
    "Arxiv_ECE": ["signal", "vlsi", "embedded", "communication", "analog", "paper", "arxiv"],
}


def setup_logging(log_path: Optional[Path] = None) -> None:
    """Configure logging to console and optional file."""
    handlers = [logging.StreamHandler()]
    if log_path:
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-8s %(message)s",
        handlers=handlers,
    )


def scan_files(root: Path) -> List[Path]:
    """Recursively find candidate files under root with allowed extensions."""
    files: List[Path] = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in EXTENSIONS:
            files.append(p)
    return files


def classify_file(p: Path) -> Optional[str]:
    """Return category name if filename/path matches keywords, else None.

    Matching is checked in the order of CATEGORY_KEYWORDS.
    """
    text = (p.name + " " + str(p.parent)).lower()
    for category, keys in CATEGORY_KEYWORDS.items():
        for k in keys:
            if k.lower() in text:
                return category
    return None


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def generate_unique_dest(dest_dir: Path, name: str) -> Path:
    """If name already exists in dest_dir, append numeric suffix before extension."""
    dest = dest_dir / name
    if not dest.exists():
        return dest

    stem = dest.stem
    suffix = dest.suffix
    counter = 1
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        candidate = dest_dir / new_name
        if not candidate.exists():
            return candidate
        counter += 1


def move_file(src: Path, dest: Path) -> None:
    """Move file from src to dest (atomic shutil.move)."""
    ensure_dir(dest.parent)
    shutil.move(str(src), str(dest))


def organize(root: Path) -> Dict[str, object]:
    """Main orchestration: scan, classify, move and collect stats."""
    logging.info("Scanning for files under %s", root)
    candidates = scan_files(root)
    logging.info("Found %d candidate files", len(candidates))

    moved = 0
    skipped = 0
    errors: List[Tuple[Path, str]] = []
    per_category: Counter = Counter()

    data_root = root / "data"
    ensure_dir(data_root)

    for idx, p in enumerate(candidates, start=1):
        try:
            logging.info("[%d/%d] Processing: %s", idx, len(candidates), p)
            category = classify_file(p)
            if not category:
                logging.info("Skipping (no matching category): %s", p)
                skipped += 1
                continue

            dest_dir = data_root / category
            ensure_dir(dest_dir)

            # If already inside destination, skip
            try:
                if p.resolve().parent == dest_dir.resolve():
                    logging.info("Already in destination, skipping: %s", p)
                    skipped += 1
                    continue
            except Exception:
                # Fall back to normal behavior if resolution fails
                pass

            dest_path = generate_unique_dest(dest_dir, p.name)
            move_file(p, dest_path)
            logging.info("Moved %s -> %s", p, dest_path)
            moved += 1
            per_category[category] += 1

        except Exception as exc:  # catch individual file errors
            logging.exception("Error moving file %s", p)
            errors.append((p, str(exc)))

    # Folder counts after organizing
    folder_counts: Dict[str, int] = {}
    for category in CATEGORY_KEYWORDS.keys():
        d = data_root / category
        if d.exists():
            folder_counts[category] = sum(1 for _ in d.iterdir() if _.is_file())

    summary = {
        "files_found": len(candidates),
        "moved": moved,
        "skipped": skipped,
        "errors": errors,
        "per_category": dict(per_category),
        "folder_counts": folder_counts,
    }
    return summary


def print_summary(summary: Dict[str, object]) -> None:
    logging.info("Organization complete")
    logging.info("Files found: %d", summary.get("files_found", 0))
    logging.info("Files moved: %d", summary.get("moved", 0))
    logging.info("Files skipped: %d", summary.get("skipped", 0))

    per_category = summary.get("per_category", {})
    if per_category:
        logging.info("Files moved per category:")
        for k, v in per_category.items():
            logging.info("  %s: %d", k, v)

    folder_counts = summary.get("folder_counts", {})
    if folder_counts:
        logging.info("Folder counts:")
        for k, v in folder_counts.items():
            logging.info("  %s: %d", k, v)

    errors = summary.get("errors", [])
    if errors:
        logging.error("Encountered %d errors:", len(errors))
        for p, msg in errors:
            logging.error("  %s -> %s", p, msg)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Organize dataset files into data/ subfolders by keywords")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Root folder to scan (default: current working dir)")
    parser.add_argument("--log", type=Path, default=None, help="Optional log file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging(args.log)

    root = args.root
    if not root.exists() or not root.is_dir():
        logging.error("Root path does not exist or is not a directory: %s", root)
        return

    logging.info("Starting organization in %s", root)
    try:
        summary = organize(root)
        print_summary(summary)
        logging.info("Done.")
    except Exception:
        logging.exception("Fatal error during organization")


if __name__ == "__main__":
    main()
