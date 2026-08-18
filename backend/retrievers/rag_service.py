"""Application service composing classification, routing, retrieval, merge, and answer generation.
Ported from capston_end/rag_service.py; only addition is threading `used_fallback` through."""
from dataclasses import dataclass

from .answer_generator import AnswerGenerator
from .base import RetrievalRequest
from .context_merger import ContextMerger
from .intent_classifier import IntentClassifier
from .prompt_builder import PromptBuilder
from .router import RetrieverRouter


@dataclass(frozen=True)
class RAGResponse:
    answer: str
    intent: object
    documents: list
    used_fallback: bool

    @property
    def strategy(self):
        return f"{self.intent.intent.value}: {self.intent.reason}"


class RAGService:
    def __init__(self):
        self.classifier, self.router, self.merger = IntentClassifier(), RetrieverRouter(), ContextMerger()
        self.prompts, self.answers = PromptBuilder(), AnswerGenerator()

    def answer_question(self, question, article=None, memory=""):
        intent = self.classifier.classify(question)
        request = RetrievalRequest(question, intent.intent.value, intent.subject, article)
        documents = [doc for retriever in self.router.route(intent) for doc in retriever.retrieve(request)]
        documents = self.merger.merge(documents)
        generated = self.answers.generate(self.prompts.build(question, intent, documents, memory), documents)
        return RAGResponse(generated.text, intent, documents, generated.used_fallback)
