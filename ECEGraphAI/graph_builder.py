from __future__ import annotations

import pickle
import re
from pathlib import Path
from typing import Dict, Iterable, List, Set

import networkx as nx

try:
    from PyPDF2 import PdfReader
except Exception:  # pragma: no cover - informative import error at runtime
    PdfReader = None

try:
    import spacy
except ImportError:
    spacy = None


DOMAIN_TERMS = {
    "BJT",
    "Transistor",
    "Amplifier",
    "Signal",
    "Filter",
    "Laplace Transform",
    "Communication System",
    "Resistor",
    "Capacitor",
    "Beta",
    "Circuit",
}

RELATIONSHIP_EXAMPLES = [
    ("BJT", "has_parameter", "Beta"),
    ("Amplifier", "uses", "Transistor"),
    ("Signal", "processed_by", "Filter"),
    ("Circuit", "contains", "Resistor"),
]


def _load_spacy_model():
    if spacy is None:
        return None
    try:
        return spacy.load("en_core_web_sm")
    except Exception:
        return spacy.blank("en")


def _read_pdf_text(path: str) -> str:
    if PdfReader is None:
        raise ImportError(
            "PyPDF2 is required to read PDF files. Install with `pip install PyPDF2`."
        )
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            texts.append(page_text)
    return "\n".join(texts)


def read_pdfs(paths: Iterable[str]) -> List[Dict]:
    """Read a list of PDF file paths and return list of document dicts."""
    docs = []
    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        text = _read_pdf_text(str(path))
        docs.append({"id": path.name, "path": str(path), "text": text})
    return docs


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def extract_concepts(text: str, concept_list: List[str] = None) -> List[str]:
    if concept_list is None:
        concept_list = ["BJT", "current gain", "amplifier", "transistor"]
    found = set()
    lower = text.lower()
    for c in concept_list:
        pattern = r"\b" + re.escape(c.lower()) + r"\b"
        if re.search(pattern, lower):
            found.add(c)
    return sorted(found)


def build_graph_from_pdfs(pdf_paths: Iterable[str], concept_list: List[str] = None) -> nx.Graph:
    docs = read_pdfs(pdf_paths)
    return build_graph_from_documents(docs, concept_list=concept_list)


def build_graph_from_documents(docs: Iterable[Dict], concept_list: List[str] = None) -> nx.Graph:
    G = nx.Graph()

    for doc in docs:
        doc_id = doc.get("id")
        text = doc.get("text", "")
        G.add_node(doc_id, type="document", text=text)
        concepts = extract_concepts(text, concept_list=concept_list)
        for c in concepts:
            if not G.has_node(c):
                G.add_node(c, type="concept")
            if G.has_edge(doc_id, c):
                G[doc_id][c]["count"] += 1
            else:
                G.add_edge(doc_id, c, type="mentions", count=1)

        for sent in _sentences(text):
            sent_concepts = extract_concepts(sent, concept_list=concept_list)
            for i in range(len(sent_concepts)):
                for j in range(i + 1, len(sent_concepts)):
                    a, b = sent_concepts[i], sent_concepts[j]
                    if G.has_edge(a, b):
                        G[a][b]["weight"] += 1
                    else:
                        G.add_edge(a, b, type="related_to", weight=1)

    return G


def _infer_node_type(term: str) -> str:
    t = term.lower()
    if any(x in t for x in ["=", "laplace", "transform", "formula"]):
        return "formulas"
    if any(x in t for x in ["resistor", "capacitor", "transistor", "bjt"]):
        return "components"
    if any(x in t for x in ["system", "signal", "communication", "topic"]):
        return "topics"
    return "concepts"


def _extract_entities_from_text(text: str, nlp, terms: Set[str]) -> Set[str]:
    entities: Set[str] = set()

    lowered = text.lower()
    for term in terms:
        if term.lower() in lowered:
            entities.add(term)

    if nlp is not None:
        doc = nlp(text)
        for ent in getattr(doc, "ents", []):
            token = ent.text.strip()
            if len(token) > 2:
                entities.add(token)

    return entities


def build_ece_graph(
    chunks: Iterable[Dict],
    graph_path: str | Path = "./graph/ece_graph.gpickle",
    neo4j_export_dir: str | Path = "./graph/neo4j_export",
) -> Dict:
    """Build ECE knowledge graph from chunk metadata and text."""
    nlp = _load_spacy_model()

    graph = nx.MultiDiGraph()

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        text = chunk.get("text", "")
        dataset = chunk.get("dataset", "unknown")

        graph.add_node(chunk_id, node_type="topics", kind="chunk", dataset=dataset)

        entities = _extract_entities_from_text(text, nlp, DOMAIN_TERMS)
        for ent in entities:
            if not graph.has_node(ent):
                graph.add_node(ent, node_type=_infer_node_type(ent), kind="entity")
            graph.add_edge(chunk_id, ent, edge_type="contains")
            graph.add_edge(ent, chunk_id, edge_type="related_to")

    for head, relation, tail in RELATIONSHIP_EXAMPLES:
        if not graph.has_node(head):
            graph.add_node(head, node_type=_infer_node_type(head), kind="entity")
        if not graph.has_node(tail):
            graph.add_node(tail, node_type=_infer_node_type(tail), kind="entity")

        edge_type = relation if relation in {"depends_on", "uses", "contains", "related_to"} else "related_to"
        graph.add_edge(head, tail, edge_type=edge_type, relation=relation)

    graph_path = Path(graph_path)
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    with graph_path.open("wb") as f:
        pickle.dump(graph, f)

    neo4j_export_dir = Path(neo4j_export_dir)
    neo4j_export_dir.mkdir(parents=True, exist_ok=True)

    nodes_csv = neo4j_export_dir / "nodes.csv"
    edges_csv = neo4j_export_dir / "edges.csv"

    with nodes_csv.open("w", encoding="utf-8") as f:
        f.write("id,node_type,kind,dataset\n")
        for node, attrs in graph.nodes(data=True):
            node_text = str(node).replace('"', '""')
            f.write(
                f'"{node_text}",'
                f'"{attrs.get("node_type", "")}",'
                f'"{attrs.get("kind", "")}",'
                f'"{attrs.get("dataset", "")}"\n'
            )

    with edges_csv.open("w", encoding="utf-8") as f:
        f.write("source,target,edge_type,relation\n")
        for source, target, attrs in graph.edges(data=True):
            source_text = str(source).replace('"', '""')
            target_text = str(target).replace('"', '""')
            f.write(
                f'"{source_text}",'
                f'"{target_text}",'
                f'"{attrs.get("edge_type", "")}",'
                f'"{attrs.get("relation", "")}"\n'
            )

    return {
        "graph": graph,
        "graph_path": str(graph_path),
        "neo4j_nodes_csv": str(nodes_csv),
        "neo4j_edges_csv": str(edges_csv),
        "total_nodes": graph.number_of_nodes(),
        "total_edges": graph.number_of_edges(),
    }