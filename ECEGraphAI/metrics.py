from __future__ import annotations

import time
from typing import Callable, Dict, Iterable, List, Optional, Tuple

try:
    import tiktoken
except ImportError:
    tiktoken = None


def precision_at_k(relevant, retrieved, k):
    if k <= 0:
        return 0.0
    retrieved_k = retrieved[:k]
    return sum(1 for r in retrieved_k if r in relevant) / float(k)


def token_count(text: str, model: str = "gpt-4") -> int:
    if not text:
        return 0
    if tiktoken is None:
        return len(text.split())
    try:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        return len(text.split())


def measure_latency(func: Callable, *args, **kwargs) -> Tuple[float, object]:
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return end - start, result


def percentage_reduction(baseline: float, improved: float) -> float:
    if baseline == 0:
        return 0.0
    return ((baseline - improved) / baseline) * 100.0


def compare_rag_vs_graphrag(
    rag_text: str,
    graphrag_text: str,
    rag_latency: float,
    graphrag_latency: float,
    rag_retrieved: Optional[List[str]] = None,
    graphrag_retrieved: Optional[List[str]] = None,
    relevant_ids: Optional[Iterable[str]] = None,
    k: int = 5,
) -> Dict:
    rag_tokens = token_count(rag_text)
    graphrag_tokens = token_count(graphrag_text)

    out = {
        "rag": {
            "token_count": rag_tokens,
            "latency_seconds": rag_latency,
        },
        "graphrag": {
            "token_count": graphrag_tokens,
            "latency_seconds": graphrag_latency,
        },
        "improvement": {
            "token_reduction_percent": percentage_reduction(rag_tokens, graphrag_tokens),
            "latency_reduction_percent": percentage_reduction(rag_latency, graphrag_latency),
        },
    }

    if rag_retrieved is not None and graphrag_retrieved is not None and relevant_ids is not None:
        relevant_set = set(relevant_ids)
        out["rag"]["precision_at_k"] = precision_at_k(relevant_set, rag_retrieved, k)
        out["graphrag"]["precision_at_k"] = precision_at_k(relevant_set, graphrag_retrieved, k)
        out["improvement"]["precision_at_k_delta"] = (
            out["graphrag"]["precision_at_k"] - out["rag"]["precision_at_k"]
        )

    return out