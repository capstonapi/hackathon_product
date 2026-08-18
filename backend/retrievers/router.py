"""Intent-to-retriever routing policy for verified, local evidence only."""
from .implementations import ArticleRetriever, ExternalNewsRetriever, GraphRetriever, OfficialBiographyRetriever, OfficialWebsiteRetriever, VectorRetriever, WikipediaRetriever
from .intent_classifier import Intent, IntentResult


class RetrieverRouter:
    def __init__(self):
        self.article, self.vector, self.news, self.graph = ArticleRetriever(), VectorRetriever(), ExternalNewsRetriever(), GraphRetriever()
        self.wikipedia, self.official = WikipediaRetriever(), OfficialWebsiteRetriever()
        self.biography = OfficialBiographyRetriever()

    def route(self, intent: IntentResult):
        # Public web search, reference pages, and single-source live news do
        # not carry our ArticleMetadata verification proof.  They must never
        # be inserted into an answer while verified-only mode is active.
        return {
            Intent.ARTICLE_CONTEXT: [self.article, self.vector],
            Intent.HISTORICAL_CONTEXT: [self.article, self.vector, self.graph],
            Intent.DEFINITION: [self.article, self.vector],
            Intent.ACRONYM: [self.article, self.vector],
            Intent.PERSON: [self.article, self.vector, self.graph],
            Intent.CURRENT_FACT: [self.article, self.vector],
            Intent.IMPACT: [self.article, self.vector],
            Intent.COMPARISON: [self.article, self.vector],
            Intent.OPINION_ANALYSIS: [self.article, self.vector],
        }[intent.intent]
