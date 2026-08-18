"""Deterministic intent classification performed before retrieval. Ported verbatim from capston_end."""
import re
from dataclasses import dataclass
from enum import Enum


class Intent(str, Enum):
    ARTICLE_CONTEXT = "ARTICLE_CONTEXT"
    HISTORICAL_CONTEXT = "HISTORICAL_CONTEXT"
    DEFINITION = "DEFINITION"
    ACRONYM = "ACRONYM"
    PERSON = "PERSON"
    IMPACT = "IMPACT"
    COMPARISON = "COMPARISON"
    CURRENT_FACT = "CURRENT_FACT"
    OPINION_ANALYSIS = "OPINION_ANALYSIS"


@dataclass(frozen=True)
class IntentResult:
    intent: Intent
    subject: str
    reason: str


class IntentClassifier:
    """Routes factual question shapes without requiring an LLM call."""

    def classify(self, question: str) -> IntentResult:
        text = " ".join(question.lower().split())
        subject = self._subject(question)
        if any(phrase in text for phrase in ("full form", "stands for", "stand for", "acronym")):
            return IntentResult(Intent.ACRONYM, subject, "acronym wording")
        if any(phrase in text for phrase in ("who is", "who was", "biography of")):
            return IntentResult(Intent.PERSON, subject, "person wording")
        if any(phrase in text for phrase in ("what is", "what are", "define", "meaning of")):
            return IntentResult(Intent.DEFINITION, subject, "definition wording")
        if any(phrase in text for phrase in ("history", "historical", "before", "previously", "timeline", "past")):
            return IntentResult(Intent.HISTORICAL_CONTEXT, subject, "historical wording")
        if any(phrase in text for phrase in ("impact", "why is this important", "why does this matter", "consequence")):
            return IntentResult(Intent.IMPACT, subject, "impact wording")
        if any(phrase in text for phrase in ("compare", "comparison", "versus", " vs ", "difference between")):
            return IntentResult(Intent.COMPARISON, subject, "comparison wording")
        if any(phrase in text for phrase in ("latest", "current", "today", "now", "recent")):
            return IntentResult(Intent.CURRENT_FACT, subject, "current fact wording")
        if any(phrase in text for phrase in ("opinion", "what do you think", "analyze", "analysis", "likely", "should")):
            return IntentResult(Intent.OPINION_ANALYSIS, subject, "opinion analysis wording")
        return IntentResult(Intent.ARTICLE_CONTEXT, subject, "default article-context wording")

    @staticmethod
    def _subject(question: str) -> str:
        for pattern in (
            r"(?:full form|acronym|meaning)\s+of\s+(.+)",
            r"(?:what does|what do)\s+(.+?)\s+stand for",
            r"(?:what is|what are|define|who is|who was|biography of)\s+(.+)",
        ):
            match = re.search(pattern, question, re.I)
            if match:
                return match.group(1).strip(" ?.!,:;")
        return question.strip(" ?.!,:;")
