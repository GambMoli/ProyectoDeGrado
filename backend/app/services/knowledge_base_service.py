from __future__ import annotations

import json
import logging
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

_TOKEN_PATTERN = re.compile(r"[a-z0-9_]+")
_STOPWORDS = {
    "a",
    "al",
    "ante",
    "como",
    "con",
    "cuál",
    "cual",
    "de",
    "del",
    "desde",
    "donde",
    "el",
    "en",
    "es",
    "esta",
    "este",
    "explica",
    "explicame",
    "funciona",
    "la",
    "las",
    "lo",
    "los",
    "me",
    "para",
    "por",
    "que",
    "qué",
    "quiero",
    "se",
    "sobre",
    "tema",
    "un",
    "una",
    "y",
}


def normalize_search_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(char for char in normalized if not unicodedata.combining(char))
    return without_accents.lower().strip()


def tokenize(value: str) -> list[str]:
    normalized = normalize_search_text(value)
    return [token for token in _TOKEN_PATTERN.findall(normalized) if token not in _STOPWORDS]


@dataclass(slots=True)
class KnowledgeDocument:
    id: str
    course: str
    unit: str
    topic: str
    subtopic: str
    content_type: str
    difficulty: str
    tags: list[str]
    source: str
    markdown_path: str
    text: str
    searchable_text: str = field(init=False)
    token_counter: Counter[str] = field(init=False)

    def __post_init__(self) -> None:
        metadata = " ".join(
            [
                self.course.replace("_", " "),
                self.unit.replace("_", " "),
                self.topic.replace("_", " "),
                self.subtopic.replace("_", " "),
                " ".join(self.tags),
                self.text,
            ]
        )
        self.searchable_text = normalize_search_text(metadata)
        self.token_counter = Counter(tokenize(self.searchable_text))

    @property
    def title(self) -> str:
        return self.topic.replace("_", " ")


@dataclass(slots=True)
class KnowledgeSearchResult:
    document: KnowledgeDocument
    score: float
    matched_terms: list[str]


class KnowledgeBaseService:
    def __init__(self, datasets_dir: str | Path) -> None:
        self.datasets_dir = Path(datasets_dir).resolve()
        self._documents = self._load_documents()

    def search(self, query: str, *, limit: int = 4) -> list[KnowledgeSearchResult]:
        query_tokens = tokenize(query)
        if not query_tokens:
            return []

        query_counter = Counter(query_tokens)
        course_hint = self.detect_course_hint(query)
        normalized_query = normalize_search_text(query)
        results: list[KnowledgeSearchResult] = []

        for document in self._documents:
            score = self._score_document(
                query_counter=query_counter,
                normalized_query=normalized_query,
                document=document,
                course_hint=course_hint,
            )
            if score <= 0:
                continue

            matched_terms = [
                token for token in query_counter if document.token_counter.get(token)
            ]
            results.append(
                KnowledgeSearchResult(
                    document=document,
                    score=score,
                    matched_terms=matched_terms,
                )
            )

        results.sort(key=lambda item: item.score, reverse=True)
        return results[:limit]

    def has_relevant_context(self, query: str) -> bool:
        return bool(self.search(query, limit=1))

    def count_documents(self) -> int:
        return len(self._documents)

    def get_course_documents(self, course: str) -> list[KnowledgeDocument]:
        return [document for document in self._documents if document.course == course]

    def get_course_outline(self, course: str) -> list[tuple[str, list[str]]]:
        unit_topics: dict[str, list[str]] = {}
        for document in self.get_course_documents(course):
            unit_topics.setdefault(document.unit, [])
            if document.topic not in unit_topics[document.unit]:
                unit_topics[document.unit].append(document.topic)
        return [(unit, topics) for unit, topics in unit_topics.items()]

    def detect_course_hint(self, query: str) -> str | None:
        normalized = normalize_search_text(query)
        if "calculo 1" in normalized:
            return "calculo_1"
        if "calculo 2" in normalized:
            return "calculo_2"
        if "metodos numericos" in normalized or "metodos numerico" in normalized:
            return "metodos_numericos"
        return None

    def _score_document(
        self,
        *,
        query_counter: Counter[str],
        normalized_query: str,
        document: KnowledgeDocument,
        course_hint: str | None,
    ) -> float:
        overlap = sum(
            min(count, document.token_counter.get(token, 0))
            for token, count in query_counter.items()
        )
        if overlap == 0:
            return 0.0

        score = overlap * 2.5

        topic_phrase = document.topic.replace("_", " ")
        unit_phrase = document.unit.replace("_", " ")
        if topic_phrase in normalized_query:
            score += 8
        if unit_phrase in normalized_query:
            score += 4
        if document.course.replace("_", " ") in normalized_query:
            score += 5
        if course_hint and document.course == course_hint:
            score += 5

        metadata_tokens = set(tokenize(f"{document.unit} {document.topic} {' '.join(document.tags)}"))
        matched_metadata = metadata_tokens.intersection(query_counter)
        score += len(matched_metadata) * 1.5
        return score

    def _load_documents(self) -> list[KnowledgeDocument]:
        if not self.datasets_dir.exists():
            logger.warning("Knowledge datasets directory does not exist: %s", self.datasets_dir)
            return []

        documents: list[KnowledgeDocument] = []
        for dataset_file in sorted(self.datasets_dir.glob("*_topics.jsonl")):
            with dataset_file.open("r", encoding="utf-8") as handle:
                for line_number, line in enumerate(handle, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                        documents.append(KnowledgeDocument(**payload))
                    except Exception as exc:
                        logger.warning(
                            "Skipping invalid knowledge row in %s line %s: %s",
                            dataset_file,
                            line_number,
                            exc,
                        )
        return documents
