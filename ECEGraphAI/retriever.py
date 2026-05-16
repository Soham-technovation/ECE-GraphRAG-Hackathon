from __future__ import annotations

import re
from typing import Dict, List, Optional, Set

import networkx as nx

from ECEGraphAI.src.embedding import EmbeddingIndexer


class Retriever:
    """Graph-based retriever."""

    def __init__(self, graph: Optional[nx.Graph] = None):
        self.graph = graph

    def set_graph(self, graph: nx.Graph):
        self.graph = graph

    def _score_text(self, text: str, terms: List[str]) -> int:
        return sum(1 for t in terms if re.search(r"\b" + re.escape(t) + r"\b", text, flags=re.I))

    def _find_snippet(self, text: str, terms: List[str]) -> str:
        sents = re.split(r"(?<=[.!?])\s+", text)
        for s in sents:
            for t in terms:
                if re.search(r"\b" + re.escape(t) + r"\b", s, flags=re.I):
                    return s.strip()
        return text.strip()[:300]

    def retrieve(self, query: str, k: int = 5) -> List[Dict]:
        if self.graph is None:
            raise ValueError("Graph is not set on the Retriever.")

        query_terms = [t.lower() for t in re.findall(r"\w+", query)]

        matched_concepts = set()
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "concept":
                name = str(node)
                for qt in query_terms:
                    if re.search(r"\b" + re.escape(qt) + r"\b", name, flags=re.I):
                        matched_concepts.add(name)
                        break

        doc_scores: Dict[str, Dict] = {}
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "document":
                text = data.get("text", "")
                score = self._score_text(text, query_terms)
                if score > 0:
                    doc_scores[node] = {"score": score, "matched_terms": query_terms}

        for c in matched_concepts:
            if c not in self.graph:
                continue
            for nbr in self.graph.neighbors(c):
                nbr_type = self.graph.nodes[nbr].get("type")
                if nbr_type == "document":
                    doc_scores.setdefault(nbr, {"score": 0, "matched_terms": []})
                    doc_scores[nbr]["score"] += 2
                elif nbr_type == "concept":
                    for doc in self.graph.neighbors(nbr):
                        if self.graph.nodes[doc].get("type") == "document":
                            doc_scores.setdefault(doc, {"score": 0, "matched_terms": []})
                            doc_scores[doc]["score"] += 1

        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1]["score"], reverse=True)
        results: List[Dict] = []
        for doc_id, info in sorted_docs[:k]:
            text = self.graph.nodes[doc_id].get("text", "")
            terms = query_terms + list(matched_concepts)
            snippet = self._find_snippet(text, terms)
            results.append({"doc_id": doc_id, "snippet": snippet, "score": info["score"]})

        return results


def _estimate_token_count(text: str) -> int:
    return len(text.split()) if text else 0


class GraphRAGRetriever:
    def __init__(self, indexer: EmbeddingIndexer, graph: nx.MultiDiGraph):
        self.indexer = indexer
        self.graph = graph

    def _collect_seed_nodes(self, similarity_results: Dict) -> Set[str]:
        seed_nodes: Set[str] = set()

        metadatas = similarity_results.get("metadatas", [[]])
        documents = similarity_results.get("documents", [[]])
        ids = similarity_results.get("ids", [[]])

        for idx, chunk_id in enumerate(ids[0] if ids else []):
            seed_nodes.add(chunk_id)
            if chunk_id in self.graph:
                for neighbor in self.graph.neighbors(chunk_id):
                    seed_nodes.add(neighbor)

            text = documents[0][idx] if documents and documents[0] and idx < len(documents[0]) else ""
            for token in text.split():
                token = token.strip(".,;:!?()[]{}")
                if token in self.graph:
                    seed_nodes.add(token)

        for md in metadatas[0] if metadatas else []:
            filename = md.get("filename") if isinstance(md, dict) else None
            if filename and filename in self.graph:
                seed_nodes.add(filename)

        return seed_nodes

    def retrieve(self, query: str, top_k: int = 5, hops: int = 1) -> Dict:
        similarity_results = self.indexer.query(query, top_k=top_k)

        retrieved_chunks = []
        ids = similarity_results.get("ids", [[]])
        docs = similarity_results.get("documents", [[]])
        metas = similarity_results.get("metadatas", [[]])
        dists = similarity_results.get("distances", [[]])

        for i, chunk_id in enumerate(ids[0] if ids else []):
            retrieved_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": docs[0][i] if docs and docs[0] and i < len(docs[0]) else "",
                    "metadata": metas[0][i] if metas and metas[0] and i < len(metas[0]) else {},
                    "distance": dists[0][i] if dists and dists[0] and i < len(dists[0]) else None,
                }
            )

        seed_nodes = self._collect_seed_nodes(similarity_results)

        visited = set(seed_nodes)
        frontier = set(seed_nodes)

        for _ in range(hops):
            next_frontier = set()
            for node in frontier:
                if node not in self.graph:
                    continue
                neighbors = set(self.graph.neighbors(node))
                if isinstance(self.graph, nx.MultiDiGraph):
                    neighbors |= set(self.graph.predecessors(node))

                for nb in neighbors:
                    if nb not in visited:
                        visited.add(nb)
                        next_frontier.add(nb)
            frontier = next_frontier

        retrieved_graph_nodes = sorted(str(node) for node in visited)

        context_parts = [item["text"] for item in retrieved_chunks if item.get("text")]
        context_parts.extend(
            str(node)
            for node in visited
            if node in self.graph and self.graph.nodes[node].get("kind") == "entity"
        )
        context = "\n\n".join(context_parts)

        return {
            "query": query,
            "retrieved_chunks": retrieved_chunks,
            "retrieved_graph_nodes": retrieved_graph_nodes,
            "context": context,
            "estimated_token_count": _estimate_token_count(context),
        }