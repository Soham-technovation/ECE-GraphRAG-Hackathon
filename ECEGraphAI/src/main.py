from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from ECEGraphAI.graph_builder import build_ece_graph
from ECEGraphAI.retriever import GraphRAGRetriever

from ECEGraphAI.src.chunking import chunk_documents
from ECEGraphAI.src.data_loader import load_documents
from ECEGraphAI.src.embedding import EmbeddingIndexer
from ECEGraphAI.src.preprocess import preprocess_documents


def _configure_logging(logs_dir: Path) -> logging.Logger:
    logs_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("ecegraphai.main")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(logs_dir / "pipeline.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def run_pipeline(project_root: Path, sample_query: str | None = None) -> dict:
    logger = _configure_logging(project_root / "logs")

    start = time.perf_counter()

    documents = load_documents(project_root / "data", log_file=project_root / "logs" / "data_loader.log")
    cleaned_docs = preprocess_documents(documents, lowercase=False)
    chunks, chunk_stats = chunk_documents(cleaned_docs, chunk_size=500, chunk_overlap=100)

    indexer = EmbeddingIndexer(
        persist_dir=project_root / "chroma_db",
        collection_name="ece_graph_ai",
        model_name="all-MiniLM-L6-v2",
    )
    embedding_stats = indexer.index_chunks(chunks)

    graph_stats = build_ece_graph(
        chunks,
        graph_path=project_root / "graph" / "ece_graph.gpickle",
        neo4j_export_dir=project_root / "graph" / "neo4j_export",
    )

    retriever = GraphRAGRetriever(indexer=indexer, graph=graph_stats["graph"])

    retrieval_result = None
    if sample_query:
        retrieval_result = retriever.retrieve(sample_query, top_k=5, hops=1)

    elapsed = time.perf_counter() - start

    summary = {
        "documents_loaded": len(documents),
        "documents_after_preprocess": len(cleaned_docs),
        "chunks_generated": chunk_stats["total_chunks"],
        "embeddings_created": embedding_stats["embeddings_created"],
        "nodes_created": graph_stats["total_nodes"],
        "edges_created": graph_stats["total_edges"],
        "execution_time_seconds": round(elapsed, 3),
        "retrieval_result": retrieval_result,
    }

    logger.info("Documents loaded: %d", summary["documents_loaded"])
    logger.info("Chunks generated: %d", summary["chunks_generated"])
    logger.info("Embeddings created: %d", summary["embeddings_created"])
    logger.info("Nodes created: %d", summary["nodes_created"])
    logger.info("Edges created: %d", summary["edges_created"])
    logger.info("Execution time: %.3f seconds", summary["execution_time_seconds"])

    if retrieval_result is not None:
        logger.info("Retrieved chunks: %d", len(retrieval_result["retrieved_chunks"]))
        logger.info("Retrieved graph nodes: %d", len(retrieval_result["retrieved_graph_nodes"]))
        logger.info("Estimated token count: %d", retrieval_result["estimated_token_count"])

    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ECEGraphAI pipeline runner")
    parser.add_argument(
        "--project_root",
        type=str,
        default=str(Path(__file__).resolve().parents[2]),
        help="Path to ECEGraphAI root",
    )
    parser.add_argument(
        "--sample_query",
        type=str,
        default="Explain BJT current gain in amplifier circuits",
        help="Query to run after indexing",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root)
    run_pipeline(project_root=project_root, sample_query=args.sample_query)


if __name__ == "__main__":
    main()
