from typing import Literal

from pydantic import BaseModel, Field


EntityType = Literal["paper", "author", "method", "dataset", "task", "metric"]
RelationType = Literal[
    "written_by",
    "proposes_method",
    "evaluated_on",
    "addresses_task",
    "uses_metric",
    "outperforms",
    "extends",
    "related_to",
]


class PaperInput(BaseModel):
    paper_id: str = Field(..., examples=["P001"])
    title: str
    authors: list[str] = []
    abstract: str


class Entity(BaseModel):
    id: str
    name: str
    type: EntityType
    source_paper_id: str | None = None


class Relation(BaseModel):
    source: str
    target: str
    type: RelationType
    evidence: str | None = None
    source_paper_id: str | None = None


class ExtractionResult(BaseModel):
    paper_id: str
    entities: list[Entity]
    relations: list[Relation]


class QueryResult(BaseModel):
    query: str
    results: list[dict]
