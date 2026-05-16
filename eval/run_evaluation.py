from __future__ import annotations

import argparse
import csv
import json
import os
import re
import statistics
import time
from pathlib import Path
from typing import List, Optional

import networkx as nx
from tqdm import tqdm

from ECEGraphAI.src.embedding import EmbeddingIndexer
from ECEGraphAI.retriever import GraphRAGRetriever
from ECEGraphAI.metrics import compare_rag_vs_graphrag, measure_latency, percentage_reduction, token_count

try:
    from bert_score import score as bert_score
except Exception:
    bert_score = None

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
    sentences = re.split(r"(?<=[.!?])\s+", text)
    out = []
    total = 0
    for sentence in sentences:
        if not sentence:
            continue
        out.append(sentence)
        total += len(sentence)
        if total >= max_chars:
            break
    return " ".join(out).strip()[:max_chars]


def _build_hf_generator(model_name: str, device: int):
    if pipeline is None:
        return None
    try:
        return pipeline("text2text-generation", model=model_name, device=device)
    except Exception:
        return None


def _call_openai_answer(model: str, prompt: str) -> Optional[str]:
    if openai is None:
        return None
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=256,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _llm_only_answer(query: str, args, hf_generator=None) -> str:
    if args.answer_backend == "openai":
        prompt = f"Answer this ECE question concisely and accurately:\n{query}"
        out = _call_openai_answer(args.openai_model, prompt)
        if out:
            return out

    if args.answer_backend == "hf" and hf_generator is not None:
        try:
            prompt = f"Answer this ECE question concisely:\n{query}"
            out = hf_generator(prompt, max_length=220, do_sample=False)
            return out[0]["generated_text"].strip()
        except Exception:
            pass

    return f"Unable to run neural LLM backend; fallback response for query: {query}"


def _answer_from_context(query: str, context: str, args, hf_generator=None) -> str:
    if args.answer_backend == "openai":
        prompt = (
            "Use only the provided context to answer concisely. "
            "If context is insufficient, state that clearly.\n\n"
            f"Question: {query}\n\nContext:\n{context}"
        )
        out = _call_openai_answer(args.openai_model, prompt)
        if out:
            return out

    if args.answer_backend == "hf" and hf_generator is not None:
        try:
            prompt = f"Question: {query}\nContext: {context}\nAnswer concisely:"
            out = hf_generator(prompt, max_length=240, do_sample=False)
            return out[0]["generated_text"].strip()
        except Exception:
            pass

    return _extractive_answer(context)


def _judge_one_answer(query: str, reference: str, answer: str, args, hf_judge=None) -> Optional[str]:
    if not reference:
        return None

    if args.llm_judge == "openai":
        prompt = (
            "Evaluate the candidate answer against the reference for correctness. "
            "Return only PASS or FAIL.\n\n"
            f"Question: {query}\n\nReference: {reference}\n\nCandidate: {answer}"
        )
        out = _call_openai_answer(args.openai_model, prompt)
        if out:
            upper = out.upper()
            if "PASS" in upper:
                return "PASS"
            if "FAIL" in upper:
                return "FAIL"
        return None

    if args.llm_judge == "hf" and hf_judge is not None:
        try:
            prompt = (
                "Judge the candidate answer against the reference. "
                "Output PASS or FAIL only.\n"
                f"Question: {query}\nReference: {reference}\nCandidate: {answer}"
            )
            out = hf_judge(prompt, max_length=32, do_sample=False)[0]["generated_text"]
            upper = out.upper()
            if "PASS" in upper:
                return "PASS"
            if "FAIL" in upper:
                return "FAIL"
        except Exception:
            return None

    return None


def _safe_bert_f1_batch(candidates: List[str], references: List[str], lang: str, rescale: bool) -> List[Optional[float]]:
    if not candidates or not references or bert_score is None:
        return [None] * len(candidates)
    try:
        _, _, f1 = bert_score(candidates, references, lang=lang, rescale_with_baseline=rescale)
        out = []
        for x in f1:
            out.append(float(x.item()) if hasattr(x, "item") else float(x))
        return out
    except Exception:
        return [None] * len(candidates)


def _safe_mean(values: List[float]) -> Optional[float]:
    return statistics.mean(values) if values else None


def load_queries(path: Path) -> List[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def run(args):
    queries = load_queries(Path(args.queries))

    indexer = EmbeddingIndexer(persist_dir=args.chroma_dir)

    graph_path = Path(args.graph_path)
    if not graph_path.exists():
        raise FileNotFoundError(f"Graph file not found: {graph_path}")
    # NetworkX read_gpickle may not be available in some installs; try safe load
    try:
        graph = nx.read_gpickle(graph_path)
    except Exception:
        import pickle

        with open(graph_path, "rb") as gf:
            graph = pickle.load(gf)

    graphrag = GraphRAGRetriever(indexer=indexer, graph=graph)

    results = []

    # optional HF pipelines
    hf_generator = None
    if args.answer_backend == "hf":
        hf_generator = _build_hf_generator(args.hf_answer_model, args.hf_device)

    hf_judge = None
    if args.llm_judge == "hf":
        hf_judge = _build_hf_generator(args.hf_judge_model, args.hf_device)

    for q in tqdm(queries, desc="Evaluating queries"):
        query_text = q.get("query", "")
        relevant = q.get("relevant_ids", "")
        relevant_ids = [x.strip() for x in relevant.split(";") if x.strip()]
        reference = q.get("reference", "").strip()

        # LLM-only pipeline
        llm_latency, llm_answer = measure_latency(_llm_only_answer, query_text, args, hf_generator)
        llm_tokens = token_count(llm_answer)

        # Basic RAG pipeline: retrieve + answer from retrieved context
        t0 = time.perf_counter()
        rag_sim = indexer.query(query_text, top_k=args.top_k)
        rag_docs = []
        docs_list = rag_sim.get("documents", [[]])
        ids_list = rag_sim.get("ids", [[]])
        for doc in (docs_list[0] if docs_list else []):
            rag_docs.append(doc)
        rag_ids = [str(x) for x in (ids_list[0] if ids_list else [])]
        rag_context = "\n\n".join(rag_docs)
        rag_answer = _answer_from_context(query_text, rag_context, args, hf_generator)
        rag_latency = time.perf_counter() - t0
        rag_tokens = token_count(rag_answer)

        # GraphRAG pipeline: retrieve + answer from graph-augmented context
        tg = time.perf_counter()
        graphrag_res = graphrag.retrieve(query_text, top_k=args.top_k, hops=args.hops)
        graphrag_context = graphrag_res.get("context", "")
        graphrag_answer = _answer_from_context(query_text, graphrag_context, args, hf_generator)
        graphrag_latency = time.perf_counter() - tg
        graphrag_tokens = token_count(graphrag_answer)
        graphrag_ids = [str(c.get("chunk_id")) for c in graphrag_res.get("retrieved_chunks", [])]

        cmp = compare_rag_vs_graphrag(
            rag_text=rag_answer,
            graphrag_text=graphrag_answer,
            rag_latency=rag_latency,
            graphrag_latency=graphrag_latency,
            rag_retrieved=rag_ids,
            graphrag_retrieved=graphrag_ids,
            relevant_ids=relevant_ids if relevant_ids else None,
            k=args.top_k,
        )

        # Accuracy evaluations (BERTScore is batched after the loop)
        bert_f1_llm = None
        bert_f1_rag = None
        bert_f1_graphrag = None

        judge_llm = _judge_one_answer(query_text, reference, llm_answer, args, hf_judge)
        judge_rag = _judge_one_answer(query_text, reference, rag_answer, args, hf_judge)
        judge_graphrag = _judge_one_answer(query_text, reference, graphrag_answer, args, hf_judge)

        results.append(
            {
                "query": query_text,
                "reference": reference,
                "llm_only_answer": llm_answer,
                "rag_answer": rag_answer,
                "graphrag_answer": graphrag_answer,
                "llm_only_tokens": llm_tokens,
                "rag_tokens": rag_tokens,
                "graphrag_tokens": graphrag_tokens,
                "llm_only_latency": llm_latency,
                "rag_latency": rag_latency,
                "graphrag_latency": graphrag_latency,
                "llm_vs_rag_token_reduction_percent": percentage_reduction(rag_tokens, llm_tokens),
                "token_reduction_percent": cmp["improvement"]["token_reduction_percent"],
                "llm_vs_rag_latency_reduction_percent": percentage_reduction(rag_latency, llm_latency),
                "latency_reduction_percent": cmp["improvement"]["latency_reduction_percent"],
                "precision_rag": cmp["rag"].get("precision_at_k"),
                "precision_graphrag": cmp["graphrag"].get("precision_at_k"),
                "bert_f1_llm_only": bert_f1_llm,
                "bert_f1_rag": bert_f1_rag,
                "bert_f1_graphrag": bert_f1_graphrag,
                "judge_llm_only": judge_llm,
                "judge_rag": judge_rag,
                "judge_graphrag": judge_graphrag,
            }
        )

    # Batch BERTScore per pipeline to avoid repeated model loads.
    if bert_score is not None:
        idx_with_ref = [i for i, r in enumerate(results) if r.get("reference")]
        if idx_with_ref:
            refs = [results[i]["reference"] for i in idx_with_ref]

            llm_candidates = [results[i]["llm_only_answer"] for i in idx_with_ref]
            rag_candidates = [results[i]["rag_answer"] for i in idx_with_ref]
            graph_candidates = [results[i]["graphrag_answer"] for i in idx_with_ref]

            llm_scores = _safe_bert_f1_batch(llm_candidates, refs, args.bert_lang, args.bert_rescale)
            rag_scores = _safe_bert_f1_batch(rag_candidates, refs, args.bert_lang, args.bert_rescale)
            graph_scores = _safe_bert_f1_batch(graph_candidates, refs, args.bert_lang, args.bert_rescale)

            for j, idx in enumerate(idx_with_ref):
                results[idx]["bert_f1_llm_only"] = llm_scores[j]
                results[idx]["bert_f1_rag"] = rag_scores[j]
                results[idx]["bert_f1_graphrag"] = graph_scores[j]

    # Aggregate summary
    token_reductions = [r["token_reduction_percent"] for r in results if r["token_reduction_percent"] is not None]
    latency_reductions = [r["latency_reduction_percent"] for r in results if r["latency_reduction_percent"] is not None]
    llm_token_reductions = [r["llm_vs_rag_token_reduction_percent"] for r in results if r.get("llm_vs_rag_token_reduction_percent") is not None]
    llm_latency_reductions = [r["llm_vs_rag_latency_reduction_percent"] for r in results if r.get("llm_vs_rag_latency_reduction_percent") is not None]

    pr_rag = [r["precision_rag"] for r in results if r["precision_rag"] is not None]
    pr_graph = [r["precision_graphrag"] for r in results if r["precision_graphrag"] is not None]
    bert_llm = [r["bert_f1_llm_only"] for r in results if r.get("bert_f1_llm_only") is not None]
    bert_rag = [r["bert_f1_rag"] for r in results if r.get("bert_f1_rag") is not None]
    bert_graph = [r["bert_f1_graphrag"] for r in results if r.get("bert_f1_graphrag") is not None]

    judge_llm_votes = [r["judge_llm_only"] for r in results if r.get("judge_llm_only") is not None]
    judge_rag_votes = [r["judge_rag"] for r in results if r.get("judge_rag") is not None]
    judge_graph_votes = [r["judge_graphrag"] for r in results if r.get("judge_graphrag") is not None]

    def pass_rate(votes: List[str]) -> Optional[float]:
        if not votes:
            return None
        return votes.count("PASS") / len(votes)

    summary = {
        "num_queries": len(results),
        "avg_token_reduction_percent_graphrag_vs_rag": _safe_mean(token_reductions),
        "median_token_reduction_percent_graphrag_vs_rag": statistics.median(token_reductions) if token_reductions else None,
        "avg_latency_reduction_percent_graphrag_vs_rag": _safe_mean(latency_reductions),
        "avg_token_reduction_percent_llm_vs_rag": _safe_mean(llm_token_reductions),
        "avg_latency_reduction_percent_llm_vs_rag": _safe_mean(llm_latency_reductions),
        "avg_precision_rag": _safe_mean(pr_rag),
        "avg_precision_graphrag": _safe_mean(pr_graph),
        "avg_bert_f1_llm_only": _safe_mean(bert_llm),
        "avg_bert_f1_rag": _safe_mean(bert_rag),
        "avg_bert_f1_graphrag": _safe_mean(bert_graph),
        "judge_pass_rate_llm_only": pass_rate(judge_llm_votes),
        "judge_pass_rate_rag": pass_rate(judge_rag_votes),
        "judge_pass_rate_graphrag": pass_rate(judge_graph_votes),
        "bonus_thresholds": {
            "judge_pass_rate_target": 0.90,
            "bertscore_f1_rescaled_target": 0.55,
            "bertscore_f1_raw_target": 0.88,
        },
        "bonus_status": {
            "judge_target_met_graphrag": (pass_rate(judge_graph_votes) is not None and pass_rate(judge_graph_votes) >= 0.90),
            "bertscore_target_met_graphrag": (
                _safe_mean(bert_graph) is not None and (
                    (_safe_mean(bert_graph) >= 0.55 and args.bert_rescale) or (_safe_mean(bert_graph) >= 0.88 and not args.bert_rescale)
                )
            ),
        },
        "judge_llm_only_votes": {"PASS": judge_llm_votes.count("PASS"), "FAIL": judge_llm_votes.count("FAIL")} if judge_llm_votes else None,
        "judge_rag_votes": {"PASS": judge_rag_votes.count("PASS"), "FAIL": judge_rag_votes.count("FAIL")} if judge_rag_votes else None,
        "judge_graphrag_votes": {"PASS": judge_graph_votes.count("PASS"), "FAIL": judge_graph_votes.count("FAIL")} if judge_graph_votes else None,
    }

    out = {"summary": summary, "per_query": results}

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default="eval/queries_sample.csv")
    parser.add_argument("--graph-path", default="graph/ece_graph.gpickle")
    parser.add_argument("--chroma-dir", default="ECEGraphAI/chroma_db")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--hops", type=int, default=1)
    parser.add_argument("--output", default="eval/evaluation_results.json")

    parser.add_argument(
        "--answer-backend",
        choices=["extractive", "hf", "openai"],
        default="extractive",
        help="Answer generation backend for LLM-only, Basic RAG, and GraphRAG answers",
    )

    parser.add_argument("--llm-judge", choices=["none", "openai", "hf"], default="none", help="Optional LLM-as-Judge backend")
    parser.add_argument("--openai-model", default="gpt-3.5-turbo")
    parser.add_argument("--hf-answer-model", default="google/flan-t5-small")
    parser.add_argument("--hf-judge-model", default="google/flan-t5-small")
    parser.add_argument("--hf-device", type=int, default=-1, help="Device index for HF pipeline (use -1 for CPU)")
    parser.add_argument("--bert-lang", default="en")
    parser.add_argument("--bert-rescale", action="store_true", help="Rescale BERTScore with baseline if available")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
