"""Intent classifier for routing requests before running the build pipeline."""

import logging

from orchestrator.model_router import ModelRouter

logger = logging.getLogger(__name__)

INTENT_QUESTION = "QUESTION"
INTENT_BUILD = "BUILD"
INTENT_AMBIGUOUS = "AMBIGUOUS"
_VALID_INTENTS = {INTENT_QUESTION, INTENT_BUILD, INTENT_AMBIGUOUS}


class IntentClassifier:
    """Classifies user intent as QUESTION, BUILD, or AMBIGUOUS."""

    def __init__(self, router: ModelRouter | None = None):
        self.router = router or ModelRouter()
        self.role = "intent_classifier"

    def classify(self, user_request: str) -> str:
        """Return one of QUESTION, BUILD, or AMBIGUOUS."""
        prompt = (
            "Classify the user's request intent for a coding assistant.\n"
            "Return exactly one word from this set only:\n"
            "QUESTION\n"
            "BUILD\n"
            "AMBIGUOUS\n\n"
            "Use QUESTION for informational requests.\n"
            "Use BUILD for implementation/modification requests.\n"
            "Use AMBIGUOUS when unclear or mixed.\n\n"
            f"User request:\n{user_request}\n"
        )

        try:
            response = self.router.generate(
                self.role,
                prompt,
                max_tokens=5,
                temperature=0,
            )
            content = (response or "").strip().upper()
            intent = content.split()[0] if content else ""
            if intent in _VALID_INTENTS:
                return intent
            logger.warning("Unexpected intent '%s', defaulting to AMBIGUOUS", content)
            return INTENT_AMBIGUOUS
        except Exception:
            logger.warning("Intent classification failed, defaulting to AMBIGUOUS", exc_info=True)
            return INTENT_AMBIGUOUS
