"""Model Router — provider-agnostic LLM gateway with YAML config and fallback."""

import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "model_config.yaml"


def _load_config() -> dict:
    with open(_CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


class ModelRouter:
    """Routes LLM calls to the right provider based on agent role."""

    def __init__(self):
        self._config = _load_config()
        self._anthropic_client = None
        self._openai_client = None

    # -- lazy client init --------------------------------------------------

    @property
    def anthropic_client(self):
        if self._anthropic_client is None:
            import anthropic
            self._anthropic_client = anthropic.Anthropic(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
            )
        return self._anthropic_client

    @property
    def openai_client(self):
        if self._openai_client is None:
            from openai import OpenAI
            self._openai_client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        return self._openai_client

    # -- public API --------------------------------------------------------

    def generate(self, role: str, prompt: str, *, max_tokens: int | None = None) -> str:
        """Send *prompt* to the model assigned to *role*, with automatic fallback."""
        models_cfg = self._config["models"]
        if role not in models_cfg:
            raise ValueError(f"Unknown role: {role}")

        cfg = models_cfg[role]
        tokens = max_tokens or cfg.get("max_tokens", 4096)

        try:
            return self._dispatch(cfg["provider"], cfg["model"], prompt, tokens)
        except Exception:
            logger.warning(
                "Primary provider failed for role=%s, falling back", role, exc_info=True,
            )
            fb = self._config["fallback"]
            return self._dispatch(fb["provider"], fb["model"], prompt, fb.get("max_tokens", 4096))

    # -- internal dispatch -------------------------------------------------

    def _dispatch(self, provider: str, model: str, prompt: str, max_tokens: int) -> str:
        logger.info("[ModelRouter] provider=%s model=%s max_tokens=%d", provider, model, max_tokens)
        if provider == "anthropic":
            return self._call_anthropic(model, prompt, max_tokens)
        if provider == "openai":
            return self._call_openai(model, prompt, max_tokens)
        if provider == "replicate":
            return self._call_replicate(model, prompt, max_tokens)
        raise ValueError(f"Unknown provider: {provider}")

    def _call_anthropic(self, model: str, prompt: str, max_tokens: int) -> str:
        response = self.anthropic_client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def _call_openai(self, model: str, prompt: str, max_tokens: int) -> str:
        response = self.openai_client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content

    def _call_replicate(self, model: str, prompt: str, max_tokens: int) -> str:
        import replicate
        output = replicate.run(
            model,
            input={"prompt": prompt, "max_new_tokens": max_tokens},
        )
        return "".join(output)

    # -- helpers -----------------------------------------------------------

    def get_safety_config(self) -> dict:
        """Return the safety section from config."""
        return self._config.get("safety", {})
