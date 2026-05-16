from __future__ import annotations

import os
import pickle
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

import networkx as nx

from ECEGraphAI.metrics import token_count
from ECEGraphAI.retriever import GraphRAGRetriever
from ECEGraphAI.src.embedding import EmbeddingIndexer

try:
    import openai
except Exception:
    openai = None

try:
    from transformers import pipeline
except Exception:
    pipeline = None


def _extractive_answer(context: str, max_chars: int = 700) -> str:
    text = (context or "").strip()
    if not text:
        return "No relevant context found."
    sents = re.split(r"(?<=[.!?])\s+", text)
    out = []
    chars = 0
    for s in sents:
        if not s:
            continue
        out.append(s)
        chars += len(s)
        if chars >= max_chars:
            break
    return " ".join(out).strip()[:max_chars]


@dataclass
class PipelineResult:
    pipeline: str
    answer: str
    latency_seconds: float
    output_tokens: int
    input_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class PipelineRunner:
    def __init__(
        self,
        chroma_dir: str = "ECEGraphAI/chroma_db",
        graph_path: str = "ECEGraphAI/graph/ece_graph.gpickle",
        top_k: int = 5,
        hops: int = 1,
        answer_backend: str = "extractive",
        hf_model: str = "google/flan-t5-small",
        openai_model: str = "gpt-4o-mini",
        input_price_per_1k: float = 0.0005,
        output_price_per_1k: float = 0.0015,
    ):
        self.top_k = top_k
        self.hops = hops
        self.answer_backend = answer_backend
        self.hf_model = hf_model
        self.openai_model = openai_model
        self.input_price_per_1k = input_price_per_1k
        self.output_price_per_1k = output_price_per_1k

        self.indexer = EmbeddingIndexer(persist_dir=chroma_dir)
        self.graph = self._load_graph(Path(graph_path))
        self.graphrag = GraphRAGRetriever(indexer=self.indexer, graph=self.graph)

        self._hf_generator = None
        if self.answer_backend == "hf" and pipeline is not None:
            try:
                self._hf_generator = pipeline("text2text-generation", model=self.hf_model, device=-1)
            except Exception:
                self._hf_generator = None

    def _load_graph(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Graph file not found: {path}")
        try:
            return nx.read_gpickle(path)
        except Exception:
            with path.open("rb") as fh:
                return pickle.load(fh)

    def _estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        in_cost = (input_tokens / 1000.0) * self.input_price_per_1k
        out_cost = (output_tokens / 1000.0) * self.output_price_per_1k
        return in_cost + out_cost

    def _call_openai(self, prompt: str) -> Optional[str]:
        if openai is None:
            return None
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        try:
            openai.api_key = api_key
            resp = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=256,
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception:
            return None

    def _generate_answer(self, query: str, context: Optional[str] = None) -> str:
        if self.answer_backend == "openai":
            if context:
                prompt = (
                    "Use only the provided context to answer the question. "
                    "If context is insufficient, say so briefly.\n\n"
                    f"Question: {query}\n\nContext:\n{context}"
                )
            else:
                prompt = f"Answer this ECE question concisely and accurately:\n{query}"
            out = self._call_openai(prompt)
            if out:
                return out

        if self.answer_backend == "hf" and self._hf_generator is not None:
            try:
                if context:
                    prompt = f"Question: {query}\nContext: {context}\nAnswer concisely:"
                else:
                    prompt = f"Answer this ECE question concisely:\n{query}"
                out = self._hf_generator(prompt, max_length=240, do_sample=False)
                return out[0]["generated_text"].strip()
            except Exception:
                pass

        if context:
            return _extractive_answer(context)
        return f"No generation backend configured. Query: {query}"

    def run_llm_only(self, query: str) -> PipelineResult:
        start = time.perf_counter()
        answer = self._generate_answer(query=query, context=None)
        latency = time.perf_counter() - start

        input_tokens = token_count(query)
        output_tokens = token_count(answer)
        total_tokens = input_tokens + output_tokens
        cost = self._estimate_cost(input_tokens, output_tokens)
        return PipelineResult(
            pipeline="LLM-only",
            answer=answer,
            latency_seconds=latency,
            output_tokens=output_tokens,
            input_tokens=input_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=cost,
        )

    def run_basic_rag(self, query: str) -> PipelineResult:
        start = time.perf_counter()
        sim = self.indexer.query(query, top_k=self.top_k)
        docs = sim.get("documents", [[]])
        context = "\n\n".join(docs[0] if docs else [])
        answer = self._generate_answer(query=query, context=context)
        latency = time.perf_counter() - start

        input_tokens = token_count(query) + token_count(context)
        output_tokens = token_count(answer)
        total_tokens = input_tokens + output_tokens
        cost = self._estimate_cost(input_tokens, output_tokens)
        return PipelineResult(
            pipeline="Basic RAG",
            answer=answer,
            latency_seconds=latency,
            output_tokens=output_tokens,
            input_tokens=input_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=cost,
        )

    def run_graphrag(self, query: str) -> PipelineResult:
        start = time.perf_counter()
        retrieved = self.graphrag.retrieve(query, top_k=self.top_k, hops=self.hops)
        context = retrieved.get("context", "")
        answer = self._generate_answer(query=query, context=context)
        latency = time.perf_counter() - start

        input_tokens = token_count(query) + token_count(context)
        output_tokens = token_count(answer)
        total_tokens = input_tokens + output_tokens
        cost = self._estimate_cost(input_tokens, output_tokens)
        return PipelineResult(
            pipeline="GraphRAG",
            answer=answer,
            latency_seconds=latency,
            output_tokens=output_tokens,
            input_tokens=input_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=cost,
        )

    def run_all(self, query: str) -> Dict[str, PipelineResult]:
        return {
            "llm_only": self.run_llm_only(query),
            "basic_rag": self.run_basic_rag(query),
            "graphrag": self.run_graphrag(query),
        }
