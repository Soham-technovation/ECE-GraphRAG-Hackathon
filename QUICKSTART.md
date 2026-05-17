# ECEGraphAI

## A Token-Efficient GraphRAG Learning Assistant

**Get ECE-GraphRAG running in 5 minutes.**

## How GraphRAG Works for You

Instead of basic keyword search (which misses concept relationships), **GraphRAG** intelligently traverses a knowledge graph to find the most relevant context:

1. **Your question enters the system** → *"Explain how BJT current gain affects amplifier performance"*
2. **The graph finds connected concepts** → BJT → current gain → amplifier → stability (graph hops)
3. **Context is retrieved smartly** → Only relevant passages, not redundant blocks
4. **Answer is generated** → With 48.6% fewer tokens than Basic RAG
5. **Metrics are displayed** → See token savings, speed, and cost in the dashboard

## What This Project Does

Compares three retrieval pipelines for ECE education:
1. **LLM-only** — Pure language model (no retrieval, baseline)
2. **Basic RAG** — Vector-based semantic search + LLM
3. **GraphRAG** — Knowledge graph-aware retrieval + LLM ← **Most Efficient**

## Prerequisites

- Python 3.9+
- ~2GB disk space (for models and vector store)

## Installation (3 commands)

### 1. Clone & Install Dependencies

```bash
cd ECE-GraphRAG-Hackathon
pip install -r requirements.txt
```

### 2. Download Models

```bash
python -m spacy download en_core_web_sm
```

### 3. Initialize (Auto-generates graph & embeddings)

```bash
python setup.py
```

**Note:** Pre-built artifacts exist, so this typically just validates your setup.

## Run the Demo

### Interactive Dashboard (Recommended)

```bash
streamlit run app.py
```

Then:
1. Check "Load Demo Query" in the sidebar
2. Click "Analyze"
3. Watch the metrics table show GraphRAG's advantages over Basic RAG

### Batch Evaluation

```bash
python eval/run_evaluation.py --queries eval/queries_sample.csv --output results.json
```

## What You'll See

The dashboard shows a comparison table:

| Pipeline | Tokens | Latency | Cost | Quality |
|----------|--------|---------|------|---------|
| LLM-only | 5200 | 3.8s | $0.06 | Medium |
| Basic RAG | 3700 | 2.7s | $0.04 | Good |
| **GraphRAG** | **1900** | **1.9s** | **$0.02** | **Excellent** |

**Key numbers:**
- ✓ GraphRAG: **48.6% fewer tokens** than Basic RAG (1900 vs 3700)
- ✓ GraphRAG: **29.6% faster** than Basic RAG
- ✓ GraphRAG: **50% cheaper** ($0.022 vs $0.044 per query)
- ✓ GraphRAG: **Better quality** (BERTScore: 0.91 vs 0.85)

## Environment Variables (Optional)

Create `.env` (copy from `.env.example`):

```bash
OPENAI_API_KEY=sk-your-key  # For OpenAI models (optional)
```

Without this, the system uses HuggingFace/Extractive models (free).

## Sample Queries (Pre-loaded)

1. "Explain how BJT current gain affects amplifier performance"
2. "What is the role of decoupling capacitors in electronic circuits?"
3. "Describe the relationship between transistor biasing and amplifier stability"

## Project Structure

```
ECE-GraphRAG-Hackathon/
├── app.py                          # Entry point
├── comparison_dashboard.py         # Streamlit dashboard (the main UI)
├── demo_config.py                  # Pre-loaded demo queries
├── setup.py                        # One-command setup
├── ECEGraphAI/
│   ├── src/
│   │   ├── main.py                # Pipeline initialization
│   │   ├── data_loader.py         # Load documents
│   │   ├── preprocess.py          # Clean text
│   │   ├── chunking.py            # Split into chunks
│   │   └── embedding.py           # Vector embeddings
│   ├── pipelines.py               # Three-pipeline runner
│   ├── retriever.py               # GraphRAG retriever
│   ├── graph_builder.py           # Knowledge graph construction
│   ├── metrics.py                 # Token counting, scoring
│   ├── graph/                     # Pre-built graph artifact
│   └── chroma_db/                 # Pre-built vector store
├── eval/
│   ├── run_evaluation.py          # Batch evaluator
│   └── queries_sample.csv         # Sample queries
├── data/
│   ├── MIT_OCW/                   # MIT course materials
│   └── NPTEL/                     # NPTEL course materials
└── README.md
```

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Chroma DB not found
```bash
python setup.py  # Regenerates artifacts
```

### Out of memory
Reduce `top_k` slider to 3 and `hops` to 1 in the dashboard sidebar.

## Next Steps

1. **Understand the Architecture** → Read `ARCHITECTURE.md`
2. **See the Results** → Check `RESULTS.md` for benchmarks
3. **Explore the Code** → Start with `comparison_dashboard.py`
4. **Run Custom Queries** → Use the dashboard's text area

## Questions?

- **How does GraphRAG work?** → See `ARCHITECTURE.md`
- **What are the metrics?** → See the dashboard metrics table
- **Can I use my own data?** → Yes, add to `data/` folder and run `setup.py`
