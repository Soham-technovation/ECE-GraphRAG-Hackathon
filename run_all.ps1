param(
    [switch]$SkipSetup,
    [switch]$SkipEval,
    [string]$AnswerBackend = "extractive",
    [string]$GraphPath = "ECEGraphAI/graph/ece_graph.gpickle",
    [string]$Queries = "eval/queries_sample.csv",
    [string]$Output = "eval/evaluation_results.json"
)

$ErrorActionPreference = "Stop"

Write-Host "=== ECE GraphRAG One-Command Runner ===" -ForegroundColor Cyan

if (-not $SkipSetup) {
    Write-Host "[1/3] Running setup.py (dependencies + artifacts check)..." -ForegroundColor Yellow
    python setup.py
}

if (-not $SkipEval) {
    Write-Host "[2/3] Running batch evaluation..." -ForegroundColor Yellow
    $env:PYTHONPATH = "."
    python eval/run_evaluation.py --queries $Queries --graph-path $GraphPath --answer-backend $AnswerBackend --output $Output
}

Write-Host "[3/3] Launching Streamlit dashboard..." -ForegroundColor Yellow
streamlit run app.py
