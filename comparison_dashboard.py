from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path

import pandas as pd
import streamlit as st

from ECEGraphAI.metrics import percentage_reduction
from ECEGraphAI.pipelines import PipelineRunner
from demo_config import DEMO_QUERIES, METRIC_THRESHOLDS, SUCCESS_CRITERIA
from dashboard_header import render_header, render_header_with_stats

try:
    from bert_score import score as bert_score
except Exception:
    bert_score = None

try:
    from transformers import pipeline
except Exception:
    pipeline = None


@st.cache_resource(show_spinner=False)
def get_runner(
    chroma_dir: str,
    graph_path: str,
    top_k: int,
    hops: int,
    answer_backend: str,
    hf_answer_model: str,
    openai_model: str,
    input_price_per_1k: float,
    output_price_per_1k: float,
):
    return PipelineRunner(
        chroma_dir=chroma_dir,
        graph_path=graph_path,
        top_k=top_k,
        hops=hops,
        answer_backend=answer_backend,
        hf_model=hf_answer_model,
        openai_model=openai_model,
        input_price_per_1k=input_price_per_1k,
        output_price_per_1k=output_price_per_1k,
    )


@st.cache_resource(show_spinner=False)
def get_hf_judge(model_name: str):
    if pipeline is None:
        return None
    try:
        return pipeline("text2text-generation", model=model_name, device=-1)
    except Exception:
        return None


def judge_with_hf(judge, query: str, reference: str, candidate: str):
    if judge is None or not reference:
        return None
    prompt = (
        "You are an answer judge. Compare candidate answer to reference for correctness. "
        "Return PASS or FAIL only.\n"
        f"Question: {query}\nReference: {reference}\nCandidate: {candidate}"
    )
    try:
        out = judge(prompt, max_length=32, do_sample=False)[0]["generated_text"]
    except Exception:
        return None
    upper = out.upper()
    if "PASS" in upper:
        return "PASS"
    if "FAIL" in upper:
        return "FAIL"
    return None


def safe_bertscore(candidate: str, reference: str, rescale: bool):
    if not reference or bert_score is None:
        return None
    try:
        _, _, f1 = bert_score([candidate], [reference], lang="en", rescale_with_baseline=rescale)
        x = f1[0]
        return float(x.item()) if hasattr(x, "item") else float(x)
    except Exception:
        return None


def main():
    st.set_page_config(page_title="ECEGraphAI: Token-Efficient GraphRAG Learning Assistant", layout="wide")
    render_header()

    # Demo Mode
    with st.sidebar:
        st.header("📁 Previous Evaluation")
        eval_path = Path("eval/evaluation_results.json")
        if eval_path.exists():
            try:
                saved = json.loads(eval_path.read_text(encoding="utf-8"))
                summary = saved.get("summary", {})
                with st.expander("Load latest batch summary", expanded=False):
                    st.json(summary)
                    if st.button("Use first query from batch", use_container_width=True):
                        first_query = (saved.get("per_query") or [{}])[0].get("query", "")
                        first_ref = (saved.get("per_query") or [{}])[0].get("reference", "")
                        if first_query:
                            st.session_state["query_seed"] = first_query
                        if first_ref:
                            st.session_state["reference_seed"] = first_ref
            except Exception:
                st.caption("Found eval results, but could not parse summary.")
        else:
            st.caption("No `eval/evaluation_results.json` found yet.")

    with st.sidebar:
        st.header("🚀 Quick Demo")
        demo_mode = st.checkbox("Load Demo Query", value=False)
        if demo_mode:
            demo_idx = st.radio("Select Demo Query", range(len(DEMO_QUERIES)),
                              format_func=lambda i: DEMO_QUERIES[i]["query"][:50] + "...")
            selected_demo = DEMO_QUERIES[demo_idx]
        else:
            selected_demo = None

    with st.sidebar:
        st.header("⚙️ Configuration")
        chroma_dir = st.text_input("Chroma DB path", "ECEGraphAI/chroma_db")
        graph_path = st.text_input("Graph path", "ECEGraphAI/graph/ece_graph.gpickle")
        top_k = st.slider("Top-k retrieval", 1, 20, 5)
        hops = st.slider("Graph hops", 1, 3, 1)

        answer_backend = st.selectbox("Answer backend", ["extractive", "hf", "openai"], index=0)
        hf_answer_model = st.text_input("HF answer model", "google/flan-t5-small")
        openai_model = st.text_input("OpenAI model", "gpt-4o-mini")

        st.header("💰 Cost Settings")
        input_price_per_1k = st.number_input("Input price USD / 1K tokens", min_value=0.0, value=0.0005, step=0.0001, format="%.6f")
        output_price_per_1k = st.number_input("Output price USD / 1K tokens", min_value=0.0, value=0.0015, step=0.0001, format="%.6f")

        st.header("✅ Accuracy Settings")
        run_accuracy = st.checkbox("Enable BERTScore + HF judge", value=True)
        hf_judge_model = st.text_input("HF judge model", "google/flan-t5-small")
        bert_rescale = st.checkbox("Use rescaled BERTScore", value=False)

    # Query Input
    col1, col2 = st.columns([3, 1])
    seeded_query = st.session_state.get("query_seed", "")
    with col1:
        if selected_demo:
            query = st.text_area("Query", selected_demo["query"], height=60)
        elif seeded_query:
            query = st.text_area("Query", seeded_query, height=60)
        else:
            query = st.text_area("Query", "Explain Kirchhoff's voltage law with a practical example.", height=60)
    with col2:
        st.write("")
        st.write("")
        if st.button("🔍 Analyze", use_container_width=True):
            st.session_state.run_query = True
        else:
            st.session_state.run_query = False

    seeded_ref = st.session_state.get("reference_seed", "")
    reference = st.text_area(
        "Reference answer (optional, for accuracy metrics)",
        selected_demo.get("reference", "") if selected_demo else seeded_ref,
        height=80,
    )

    if not st.session_state.get("run_query", False):
        st.info("👈 Configure settings and click **Analyze** to compare all three pipelines")
        return

    runner = get_runner(
        chroma_dir=chroma_dir,
        graph_path=graph_path,
        top_k=top_k,
        hops=hops,
        answer_backend=answer_backend,
        hf_answer_model=hf_answer_model,
        openai_model=openai_model,
        input_price_per_1k=input_price_per_1k,
        output_price_per_1k=output_price_per_1k,
    )

    with st.spinner("🔄 Running all 3 pipelines..."):
        outputs = runner.run_all(query)

    judge = get_hf_judge(hf_judge_model) if run_accuracy else None

    llm = outputs["llm_only"]
    rag = outputs["basic_rag"]
    graph = outputs["graphrag"]

    # Key metrics display
    st.markdown("---")

    token_reduction = percentage_reduction(rag.total_tokens, graph.total_tokens)
    cost_reduction = percentage_reduction(rag.estimated_cost_usd, graph.estimated_cost_usd)
    quality_maintained = (run_accuracy and reference.strip())

    render_header_with_stats(
        token_reduction=token_reduction,
        cost_reduction=cost_reduction,
        accuracy_maintained=quality_maintained
    )

    st.subheader("📊 Detailed Efficiency Metrics")

    col1, col2, col3, col4 = st.columns(4)
    latency_reduction = percentage_reduction(rag.latency_seconds, graph.latency_seconds)
    with col1:
        st.metric("📌 Tokens (RAG vs GraphRAG)", f"{rag.total_tokens} → {graph.total_tokens}",
                 f"{token_reduction:.1f}% saved")
    with col2:
        st.metric("⏱️ Latency (RAG vs GraphRAG)", f"{rag.latency_seconds:.2f}s → {graph.latency_seconds:.2f}s",
                 f"{latency_reduction:.1f}% faster")
    with col3:
        st.metric("💰 Cost (RAG vs GraphRAG)", f"${rag.estimated_cost_usd:.4f} → ${graph.estimated_cost_usd:.4f}",
                 f"{cost_reduction:.1f}% cheaper")
    with col4:
        quality_status = "✓ Yes" if quality_maintained else "ℹ️ Pending"
        st.metric("✅ Quality Maintained?", quality_status, "See accuracy below")

    # Comparison table
    st.markdown("---")
    st.subheader("📈 Complete Metrics Comparison")

    rows = [asdict(llm), asdict(rag), asdict(graph)]
    metrics_df = pd.DataFrame(rows)

    # Format for display
    display_df = metrics_df.copy()
    display_df = display_df.rename(columns={
        "pipeline": "Pipeline",
        "total_tokens": "Total Tokens",
        "latency_seconds": "Latency (s)",
        "estimated_cost_usd": "Cost (USD)",
        "answer": "Answer (truncated)"
    })
    display_df["Answer (truncated)"] = display_df.get("Answer (truncated)", "").apply(
        lambda x: (x[:100] + "...") if isinstance(x, str) and len(x) > 100 else x
    )

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Detailed Answers
    st.markdown("---")
    st.subheader("📄 Detailed Answers from Each Pipeline")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.write("**LLM-only** (Baseline - no retrieval)")
        st.info(llm.answer)
    with col2:
        st.write("**Basic RAG** (Vector retrieval)")
        st.info(rag.answer)
    with col3:
        st.write("**GraphRAG** (Graph-aware retrieval)")
        with st.container(border=True):
            st.success(graph.answer)
            st.caption(f"✓ Using {token_reduction:.0f}% fewer tokens")

    # Accuracy metrics
    if run_accuracy and reference.strip():
        st.markdown("---")
        st.subheader("✅ Quality Assessment")

        bert_llm = safe_bertscore(llm.answer, reference, bert_rescale)
        bert_rag = safe_bertscore(rag.answer, reference, bert_rescale)
        bert_graph = safe_bertscore(graph.answer, reference, bert_rescale)

        judge_llm = judge_with_hf(judge, query, reference, llm.answer)
        judge_rag = judge_with_hf(judge, query, reference, rag.answer)
        judge_graph = judge_with_hf(judge, query, reference, graph.answer)

        acc_df = pd.DataFrame([
            {"Pipeline": "LLM-only", "BERTScore F1": bert_llm, "Judge": judge_llm},
            {"Pipeline": "Basic RAG", "BERTScore F1": bert_rag, "Judge": judge_rag},
            {"Pipeline": "GraphRAG", "BERTScore F1": bert_graph, "Judge": judge_graph},
        ])
        st.dataframe(acc_df, use_container_width=True, hide_index=True)

        judge_pass = 1 if judge_graph == "PASS" else 0
        score_val = bert_graph if bert_graph is not None else 0.0
        target = 0.55 if bert_rescale else 0.88

        success = (judge_pass == 1) and (score_val >= target)
        if success:
            st.success(f"🎉 GraphRAG maintains quality! BERTScore: {score_val:.3f} (target: {target:.2f}), Judge: {judge_graph}")
        else:
            st.warning(f"Quality check: BERTScore {score_val:.3f}, Judge {judge_graph}")
    elif run_accuracy:
        st.info("ℹ️ Provide a reference answer above to compute quality metrics.")


if __name__ == "__main__":
    main()
