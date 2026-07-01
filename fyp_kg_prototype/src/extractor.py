import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from .schemas import Entity, ExtractionResult, PaperInput, Relation


load_dotenv()


SYSTEM_PROMPT = """
You are an academic information extraction system.
Extract entities and relations from NLP/ML paper metadata and abstract.

Allowed entity types:
- paper
- author
- method
- dataset
- task
- metric

Allowed relation types:
- written_by
- proposes_method
- evaluated_on
- addresses_task
- uses_metric
- outperforms
- extends
- related_to

Return only valid JSON with this schema:
{
  "entities": [
    {
      "id": "string",
      "name": "string",
      "type": "paper|author|method|dataset|task|metric",
      "source_paper_id": "string"
    }
  ],
  "relations": [
    {
      "source": "entity_id",
      "target": "entity_id",
      "type": "relation_type",
      "evidence": "short text evidence",
      "source_paper_id": "string"
    }
  ]
}

Rules:
1. The paper itself must be an entity.
2. Every author must be an author entity.
3. Every relation source and target must refer to existing entity ids.
4. Use stable lowercase ids with underscores.
5. Do not invent datasets, metrics, or tasks if they are not supported by the text.
"""


class LLMExtractor:
    def __init__(self) -> None:
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL") or None
        self.use_json_mode = os.getenv("LLM_JSON_MODE", "true").lower() == "true"

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is missing. Please set it in your .env file.")

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=self.base_url,
        )

    def extract(self, paper: PaperInput) -> ExtractionResult:
        user_prompt = self._build_user_prompt(paper)
        request_args = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
        }
        if self.use_json_mode:
            request_args["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**request_args)
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("LLM returned empty content.")

        raw = self._parse_json_content(content)
        return self._to_result(paper.paper_id, raw)

    def _build_user_prompt(self, paper: PaperInput) -> str:
        return f"""
Paper ID: {paper.paper_id}
Title: {paper.title}
Authors: {", ".join(paper.authors)}
Abstract:
{paper.abstract}
"""

    def _parse_json_content(self, content: str) -> dict[str, Any]:
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            cleaned = content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned.removeprefix("```json").strip()
            elif cleaned.startswith("```"):
                cleaned = cleaned.removeprefix("```").strip()
            if cleaned.endswith("```"):
                cleaned = cleaned.removesuffix("```").strip()
            return json.loads(cleaned)

    def _to_result(self, paper_id: str, raw: dict[str, Any]) -> ExtractionResult:
        entities = [Entity(**item) for item in raw.get("entities", [])]
        relations = [Relation(**item) for item in raw.get("relations", [])]
        return ExtractionResult(
            paper_id=paper_id,
            entities=entities,
            relations=relations,
        )
