"""Base Agent — abstract base class for all LLM-powered agents."""

from abc import ABC, abstractmethod

from orchestrator.model_router import ModelRouter


class BaseAgent(ABC):
    """Every agent inherits from this and gets a shared ModelRouter."""

    def __init__(self, router: ModelRouter | None = None):
        self.router = router or ModelRouter()

    @property
    @abstractmethod
    def role(self) -> str:
        """The config role name used to select the LLM model."""
        ...

    def call_llm(self, prompt: str, *, max_tokens: int | None = None) -> str:
        """Send *prompt* through the router using this agent's role."""
        return self.router.generate(self.role, prompt, max_tokens=max_tokens)
