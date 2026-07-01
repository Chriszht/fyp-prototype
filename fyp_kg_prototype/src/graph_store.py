import json
import re
from pathlib import Path

import networkx as nx

from .schemas import Entity, ExtractionResult, Relation


class GraphStore:
    def __init__(self, storage_path: str = "data/kg.json") -> None:
        self.storage_path = Path(storage_path)
        self.graph = nx.MultiDiGraph()
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.load()

    def add_extraction(self, result: ExtractionResult) -> None:
        for entity in result.entities:
            normalized_name = self._normalize_name(entity.name)
            if entity.id not in self.graph:
                self.graph.add_node(
                    entity.id,
                    name=entity.name,
                    normalized_name=normalized_name,
                    type=entity.type,
                    source_paper_id=entity.source_paper_id,
                )
            else:
                self.graph.nodes[entity.id]["name"] = entity.name
                self.graph.nodes[entity.id]["normalized_name"] = normalized_name
                self.graph.nodes[entity.id]["type"] = entity.type

        for relation in result.relations:
            if relation.source in self.graph and relation.target in self.graph:
                self.graph.add_edge(
                    relation.source,
                    relation.target,
                    relation_type=relation.type,
                    evidence=relation.evidence,
                    source_paper_id=relation.source_paper_id,
                )
        self.save()

    def search_entities(self, keyword: str) -> list[dict]:
        keyword_norm = self._normalize_name(keyword)
        matches = []
        for node_id, data in self.graph.nodes(data=True):
            name = data.get("name", "")
            normalized_name = data.get("normalized_name", "")
            if keyword_norm in normalized_name:
                matches.append({"id": node_id, **data})
        return matches

    def papers_using_dataset(self, dataset_name: str) -> list[dict]:
        dataset_nodes = self._find_nodes_by_name_and_type(dataset_name, "dataset")
        return self._papers_connected_to(dataset_nodes)

    def methods_for_task(self, task_name: str) -> list[dict]:
        task_nodes = self._find_nodes_by_name_and_type(task_name, "task")
        results = []
        for task_id in task_nodes:
            for source, target, edge_data in self.graph.in_edges(task_id, data=True):
                if edge_data.get("relation_type") in {"addresses_task", "related_to"}:
                    source_data = self.graph.nodes[source]
                    if source_data.get("type") == "method":
                        results.append({"method_id": source, **source_data, "evidence": edge_data.get("evidence")})
        return results

    def graph_summary(self) -> dict:
        entity_count_by_type: dict[str, int] = {}
        relation_count_by_type: dict[str, int] = {}

        for _, data in self.graph.nodes(data=True):
            entity_type = data.get("type", "unknown")
            entity_count_by_type[entity_type] = entity_count_by_type.get(entity_type, 0) + 1

        for _, _, data in self.graph.edges(data=True):
            relation_type = data.get("relation_type", "unknown")
            relation_count_by_type[relation_type] = relation_count_by_type.get(relation_type, 0) + 1

        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "entity_count_by_type": entity_count_by_type,
            "relation_count_by_type": relation_count_by_type,
        }

    def export_json(self) -> dict:
        nodes = [{"id": node_id, **data} for node_id, data in self.graph.nodes(data=True)]
        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({"source": source, "target": target, **data})
        return {"nodes": nodes, "edges": edges}

    def save(self) -> None:
        self.storage_path.write_text(
            json.dumps(self.export_json(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def load(self) -> None:
        if not self.storage_path.exists():
            return
        raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        for node in raw.get("nodes", []):
            node_id = node.pop("id")
            self.graph.add_node(node_id, **node)
        for edge in raw.get("edges", []):
            source = edge.pop("source")
            target = edge.pop("target")
            self.graph.add_edge(source, target, **edge)

    def _papers_connected_to(self, node_ids: list[str]) -> list[dict]:
        papers = {}
        for node_id in node_ids:
            for source, target, edge_data in self.graph.in_edges(node_id, data=True):
                for candidate_id in [source, edge_data.get("source_paper_id")]:
                    if candidate_id and candidate_id in self.graph:
                        candidate = self.graph.nodes[candidate_id]
                        if candidate.get("type") == "paper":
                            papers[candidate_id] = {"paper_id": candidate_id, **candidate}
        return list(papers.values())

    def _find_nodes_by_name_and_type(self, name: str, entity_type: str) -> list[str]:
        name_norm = self._normalize_name(name)
        matches = []
        for node_id, data in self.graph.nodes(data=True):
            if data.get("type") != entity_type:
                continue
            if name_norm in data.get("normalized_name", ""):
                matches.append(node_id)
        return matches

    def _normalize_name(self, name: str) -> str:
        name = name.lower().strip()
        name = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", name)
        return re.sub(r"\s+", " ", name).strip()
