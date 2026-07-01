# Academic Knowledge Graph Construction Prototype

This project is an initial prototype for automated knowledge graph construction from academic papers. It takes paper metadata and abstracts as input, uses an LLM API to extract academic entities and relations, stores the extracted results as a graph structure, and exposes query endpoints through a FastAPI backend.

The current implementation focuses on the core pipeline required for an early-stage academic knowledge graph system:

1. Paper metadata and abstract ingestion.
2. LLM-based entity and relation extraction.
3. Structured validation of extracted entities and relations.
4. JSON-based graph storage using `networkx`.
5. API endpoints for graph inspection and basic querying.

## System Overview

The prototype is designed around a modular pipeline:

```text
Paper metadata and abstract
  -> LLM extraction
  -> structured entities and relations
  -> graph storage
  -> API-based query and inspection
```

The system currently supports the following entity types:

| Entity Type | Description |
|---|---|
| `paper` | Academic paper or publication record |
| `author` | Paper author |
| `method` | Model, algorithm, framework, or technical approach |
| `dataset` | Dataset used for training, evaluation, or comparison |
| `task` | Research task, such as question answering or machine translation |
| `metric` | Evaluation metric, such as accuracy, F1 score, or BLEU |

The system currently supports the following relation types:

| Relation Type | Description |
|---|---|
| `written_by` | Connects a paper to its authors |
| `proposes_method` | Indicates that a paper proposes a method |
| `evaluated_on` | Connects a paper or method to an evaluation dataset |
| `addresses_task` | Connects a method or paper to a research task |
| `uses_metric` | Connects a paper or method to an evaluation metric |
| `outperforms` | Represents a comparative performance relation |
| `extends` | Indicates extension of an existing method or study |
| `related_to` | Represents a general semantic relation |

## Project Structure

```text
fyp_kg_prototype/
  data/
    sample_papers.json      # Sample paper metadata and abstracts
    kg.json                 # Generated graph data after extraction
  src/
    __init__.py
    app.py                  # FastAPI application and API routes
    extractor.py            # LLM-based extraction logic
    graph_store.py          # Graph storage and query logic
    schemas.py              # Pydantic data models
    evaluate.py             # Basic evaluation utilities
  .env                      # Local API configuration, not intended for sharing
  .env.example              # Configuration template
  requirements.txt          # Python dependencies
  README.md                 # Project documentation
```

## Installation

Create and activate a virtual environment before installing dependencies:

```powershell
cd fyp_kg_prototype
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuration

Copy the configuration template:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure the model provider:

```text
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=
OPENAI_MODEL=gpt-4o-mini
LLM_JSON_MODE=true
```

For the official OpenAI API, `OPENAI_BASE_URL` can remain empty.

For OpenAI-compatible providers such as Arli AI, DeepSeek, or OpenRouter, configure the provider-specific base URL and model name:

```text
OPENAI_API_KEY=your_provider_api_key
OPENAI_BASE_URL=provider_base_url
OPENAI_MODEL=provider_model_name
LLM_JSON_MODE=false
```

`LLM_JSON_MODE` controls whether the request uses OpenAI-style JSON response formatting. Some third-party providers do not support this parameter. When it is set to `false`, the system still instructs the model to return JSON and attempts to parse both plain JSON and JSON wrapped in Markdown code blocks.

## Running the Server

Start the FastAPI backend from the project root directory:

```powershell
uvicorn src.app:app --reload
```

After the server starts, open the API documentation page:

```text
http://127.0.0.1:8000/docs
```

FastAPI also provides the OpenAPI specification at:

```text
http://127.0.0.1:8000/openapi.json
```

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | `GET` | Health check for the running backend |
| `/extract` | `POST` | Extract entities and relations from a single paper |
| `/load-sample` | `POST` | Run extraction on papers in `data/sample_papers.json` |
| `/summary` | `GET` | Return graph-level statistics |
| `/entities/search` | `GET` | Search entities by keyword |
| `/query/papers-by-dataset` | `GET` | Find papers associated with a dataset |
| `/query/methods-by-task` | `GET` | Find methods associated with a task |
| `/graph` | `GET` | Export the full graph as JSON |

## Example Request

The `/extract` endpoint accepts a single paper record:

```json
{
  "paper_id": "P003",
  "title": "Example Paper",
  "authors": ["Alice Zhang", "Bob Li"],
  "abstract": "This paper proposes a graph neural network method for relation extraction and evaluates it on the TACRED dataset using F1 score."
}
```

A successful response contains extracted entities and relations in structured JSON format. The result is also added to the local graph store.

## Basic Testing Flow

Use the interactive API documentation page at `/docs` to test the current implementation:

1. Call `GET /` to confirm that the backend is running.
2. Call `POST /extract` with a short paper example.
3. Call `GET /summary` to inspect the number of graph nodes and edges.
4. Call `GET /entities/search` with a keyword such as `BERT` or `Transformer`.
5. Call `GET /graph` to inspect the full graph output.

When using a free or trial API plan, single-paper extraction through `/extract` is recommended for initial testing. Batch extraction through `/load-sample` may trigger provider-side rate or concurrency limits.

## Evaluation Utilities

The `src/evaluate.py` file contains basic utilities for computing precision, recall, and F1 score. These functions are intended for later evaluation against a manually annotated gold set.

At the current stage, the evaluation module provides the calculation logic but does not include a complete annotated benchmark dataset.

## Current Scope

| Topic Requirement | Current Status |
|---|---|
| LLM API-based extraction | Implemented |
| Academic entity extraction | Implemented for predefined entity types |
| Academic relation extraction | Implemented for predefined relation types |
| Duplicate resolution | Basic name normalization only |
| Queryable graph | Implemented with JSON-backed `networkx` graph storage |
| Web interface | Available through FastAPI Swagger UI |
| Evaluation | Basic metric utilities provided; gold-set evaluation not yet implemented |

## Future Work

The current prototype implements the minimum pipeline for academic knowledge graph construction. Further development can focus on system robustness, graph quality, and evaluation depth:

1. Replace JSON-based graph storage with Neo4j or another graph database to support more expressive graph queries.
2. Improve entity normalization and duplicate resolution to merge equivalent names, abbreviations, and aliases.
3. Expand the paper dataset to cover a larger set of NLP/ML publications.
4. Add LLM response caching to reduce repeated API calls and improve reproducibility.
5. Build a manually annotated gold set for evaluating entity and relation extraction quality.
6. Extend the evaluation module to report precision, recall, and F1 score separately for entities and relations.
7. Add a graph visualization interface using Streamlit, React, PyVis, or another suitable frontend framework.
8. Add batch import support for paper abstracts or selected full-text sections.
