from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Document:
    title: str
    source: str
    url: str
    content: str
    relevance_score: float
    source_type: str
    published_at: str = ""
    retrieved_at: str = ""
    trust_score: float = 0.0


@dataclass(frozen=True)
class RetrievalRequest:
    question: str
    intent: str
    subject: str
    article: dict[str, Any] | None = None


class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, request: RetrievalRequest) -> list[Document]:
        """Return normalized documents only; provider response shapes stay private."""
        raise NotImplementedError
