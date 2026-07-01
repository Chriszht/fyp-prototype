import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

from .extractor import LLMExtractor
from .graph_store import GraphStore
from .schemas import ExtractionResult, PaperInput


app = FastAPI(
    title="Academic Knowledge Graph Prototype",
    description="A minimal prototype for automated knowledge graph construction from academic papers.",
    version="0.1.0",
)

graph_store = GraphStore(storage_path="data/kg.json")
extractor = LLMExtractor()


@app.get("/")
def root() -> dict:
    return {
        "message": "Academic Knowledge Graph Prototype is running.",
        "docs": "/docs",
    }


@app.get("/summary")
def summary() -> dict:
    return graph_store.graph_summary()


@app.post("/extract", response_model=ExtractionResult)
def extract_one_paper(paper: PaperInput) -> ExtractionResult:
    try:
        result = extractor.extract(paper)
        graph_store.add_extraction(result)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/load-sample")
def load_sample() -> dict:
    sample_path = Path("data/sample_papers.json")
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail="data/sample_papers.json not found.")

    papers = json.loads(sample_path.read_text(encoding="utf-8"))
    results = []
    for item in papers:
        paper = PaperInput(**item)
        result = extractor.extract(paper)
        graph_store.add_extraction(result)
        results.append(result.model_dump())

    return {
        "message": f"Loaded {len(results)} sample papers.",
        "summary": graph_store.graph_summary(),
        "extractions": results,
    }


@app.get("/entities/search")
def search_entities(q: str) -> dict:
    return {
        "query": q,
        "results": graph_store.search_entities(q),
    }


@app.get("/query/papers-by-dataset")
def papers_by_dataset(dataset: str) -> dict:
    return {
        "query": f"papers using dataset: {dataset}",
        "results": graph_store.papers_using_dataset(dataset),
    }


@app.get("/query/methods-by-task")
def methods_by_task(task: str) -> dict:
    return {
        "query": f"methods for task: {task}",
        "results": graph_store.methods_for_task(task),
    }


@app.get("/graph")
def export_graph() -> dict:
    return graph_store.export_json()
