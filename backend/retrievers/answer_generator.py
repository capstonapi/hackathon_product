"""
Single LLM boundary with an extractive fallback. Ported from
capston_end/answer_generator.py, now via gemini_client.

The only behavioral addition vs. the original: `generate()` also reports
whether the extractive fallback was used, so the chat API can surface a
`trust_status` without touching the prompt or the generation call itself.
"""
import logging
import time
from dataclasses import dataclass

from services.gemini_client import get_model

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeneratedAnswer:
    text: str
    used_fallback: bool


class AnswerGenerator:
    def generate(self, prompt, documents) -> GeneratedAnswer:
        started = time.monotonic()
        for attempt in range(3):
            try:
                response = get_model().generate_content(prompt)
                text = (getattr(response, "text", None) or "").strip()
                if not text:
                    raise RuntimeError("empty_model_response")
                logger.info("llm_complete model=%s latency_ms=%d retries=%d", "configured", int((time.monotonic() - started) * 1000), attempt)
                return GeneratedAnswer(text, used_fallback=False)
            except Exception as error:
                # Do not log prompts, retrieved article text, or credentials.
                logger.warning("llm_attempt_failed failure_type=%s attempt=%d", type(error).__name__, attempt + 1)
                if attempt < 2:
                    time.sleep(0.5 * (2 ** attempt))

        logger.error("llm_fallback latency_ms=%d", int((time.monotonic() - started) * 1000))
        if not documents:
            return GeneratedAnswer("No reliable evidence was retrieved for this question. Please try again later or ask a more specific question.", used_fallback=True)
        text = "I couldn't generate a live AI synthesis. Here are the retrieved source excerpts:\n\n" + "\n\n".join(f"[{i}] **{doc.title}** ({doc.source}): {doc.content}" for i, doc in enumerate(documents[:3], 1))
        return GeneratedAnswer(text, used_fallback=True)
