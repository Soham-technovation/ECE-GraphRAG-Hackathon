# Evaluation instructions

Run the evaluation harness to measure token reduction, retrieval precision, and latency between Basic RAG and GraphRAG.

Install updated dependencies (from `ECEGraphAI/requirements.txt`):

```bash
pip install -r ECEGraphAI/requirements.txt
```

Run the 3-pipeline evaluation (uses `ECEGraphAI/graph/ece_graph.gpickle` and a chroma DB in `ECEGraphAI/chroma_db`):

```bash
python eval/run_evaluation.py --queries eval/queries_sample.csv --graph-path ECEGraphAI/graph/ece_graph.gpickle --output eval/evaluation_results.json
```

The script writes `eval/evaluation_results.json` with per-query metrics and an aggregated summary.

Optional accuracy evaluation flags
---------------------------------

The harness supports BERTScore and an optional LLM-as-a-Judge. To enable these features:

- Add a `reference` column to your `queries.csv` with the ground-truth answer text.
- Use `--llm-judge openai` to run an LLM judge via OpenAI (requires `OPENAI_API_KEY` in environment).
- Use `--llm-judge hf` to run a local Hugging Face text2text judge (will download the model if necessary).

Answer generation backend options:
- `--answer-backend extractive`: no neural generation (fast baseline, uses extractive context answer)
- `--answer-backend hf`: local Hugging Face generation model for all 3 pipelines
- `--answer-backend openai`: OpenAI generation for all 3 pipelines

Example with BERTScore and HF judge:

```bash
python eval/run_evaluation.py --queries eval/queries_sample.csv --graph-path ECEGraphAI/graph/ece_graph.gpickle \
	--answer-backend hf --hf-answer-model google/flan-t5-small \
	--llm-judge hf --hf-judge-model google/flan-t5-small --bert-rescale --output eval/evaluation_results.json
```

If using OpenAI as the judge, set your API key and choose the model:

```bash
export OPENAI_API_KEY="sk-..."
python eval/run_evaluation.py --answer-backend openai --llm-judge openai --openai-model gpt-4 --queries eval/queries_sample.csv
```

Notes:
- BERTScore requires the `bert-score` package (already present in `ECEGraphAI/requirements.txt`).
- HF judge requires `transformers` (also listed in requirements). Models are downloaded the first time and may increase runtime.
- The judge returns coarse PASS/FAIL votes; use BERTScore F1 for continuous similarity metrics.

Interactive comparison dashboard
--------------------------------

Use the main side-by-side dashboard for one-query comparison and live metrics:

```bash
streamlit run comparison_dashboard.py
```
