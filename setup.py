#!/usr/bin/env python3
"""One-command setup for ECE-GraphRAG-Hackathon.
Initializes all required artifacts: embeddings, graph, spacy model.
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command with error handling."""
    print(f"\n>> {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=False)
        print(f"[OK] {description} complete")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] {description} failed: {e}")
        return False


def check_artifacts():
    """Check if required artifacts exist."""
    project_root = Path(__file__).parent
    chroma_db = project_root / "ECEGraphAI" / "chroma_db"
    graph_file = project_root / "ECEGraphAI" / "graph" / "ece_graph.gpickle"

    chroma_exists = chroma_db.exists() and len(list(chroma_db.glob("*"))) > 0
    graph_exists = graph_file.exists()

    return chroma_exists, graph_exists


def main():
    """Main setup flow."""
    print("=" * 70)
    print("ECE-GraphRAG-Hackathon Setup")
    print("=" * 70)

    project_root = Path(__file__).parent

    # Check if artifacts exist
    chroma_exists, graph_exists = check_artifacts()

    if chroma_exists and graph_exists:
        print("\n[OK] All artifacts already exist! Skipping initialization.")
        print("\nYou can now run: streamlit run app.py")
        return 0

    # Install dependencies
    if not run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installing dependencies"
    ):
        return 1

    # Download spacy model
    if not run_command(
        f"{sys.executable} -m spacy download en_core_web_sm",
        "Downloading spaCy model"
    ):
        print("[WARN] spaCy model download failed, but continuing...")

    # Run initialization pipeline
    if not chroma_exists or not graph_exists:
        init_script = project_root / "ECEGraphAI" / "src" / "main.py"
        if not run_command(
            f"{sys.executable} {init_script}",
            "Initializing graph and embeddings"
        ):
            return 1

    # Verify all components
    print("\n>> Verifying installation...")
    try:
        import chromadb
        import networkx as nx
        from sentence_transformers import SentenceTransformer
        import streamlit
        print("[OK] All dependencies loaded successfully")
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        return 1

    # Final check
    chroma_exists, graph_exists = check_artifacts()
    if not (chroma_exists and graph_exists):
        print("\n[ERROR] Initialization incomplete. Artifacts still missing.")
        return 1

    print("\n" + "=" * 70)
    print("[OK] Setup complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Run the demo dashboard:")
    print("     streamlit run app.py")
    print("\n  2. Or run evaluation with:")
    print("     python eval/run_evaluation.py --queries eval/queries_sample.csv")
    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
