"""Q&A responder that answers user questions with workspace context."""

import logging

from orchestrator.model_router import ModelRouter
from tools.workspace_loader import WorkspaceLoader

logger = logging.getLogger(__name__)


class QAResponder:
    """Answers informational questions without running the full agent pipeline."""

    def __init__(self, router: ModelRouter | None = None):
        self.router = router or ModelRouter()
        self.role = "qa_responder"

    def answer(self, question: str) -> str:
        """Return a direct answer using current workspace context."""
        workspace_context = WorkspaceLoader().format_for_prompt()

        prompt = f"""You are a coding assistant answering user questions about a codebase.

Use the provided workspace context to answer accurately.
If context is missing, say what is missing briefly.

Workspace context:
{workspace_context}

User question:
{question}
"""

        try:
            response = self.router.generate(
                self.role,
                prompt,
                max_tokens=800,
                temperature=0.2,
            )
            return (response or "").strip()
        except Exception:
            logger.warning("QA response generation failed", exc_info=True)
            return (
                "I could not generate an answer right now due to an upstream model error. "
                "Please try again."
            )
