from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


class EmbeddingIndexer:
    def __init__(
        self,
        persist_dir: str | Path = "./chroma_db",
        collection_name: str = "ece_graphrag_chunks",
        model_name: str = "all-MiniLM-L6-v2",
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(collection_name)
        self.model = SentenceTransformer(model_name)

    def index_chunks(self, chunks: List[Dict]) -> Dict:
        ids = [chunk["chunk_id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        metadatas = [
            {
                "source": chunk.get("source", ""),
                "dataset": chunk.get("dataset", "unknown"),
                "filename": chunk.get("filename", ""),
            }
            for chunk in chunks
        ]

        embeddings = self.model.encode(texts, show_progress_bar=True).tolist()
        self.collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

        return {
            "embeddings_created": len(embeddings),
            "collection_name": self.collection.name,
            "persist_dir": str(self.persist_dir),
        }

    def query(self, query_text: str, top_k: int = 5) -> Dict:
        query_embedding = self.model.encode([query_text]).tolist()[0]
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results
