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

    def generate(
        self,
        role: str,
        prompt: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """Send *prompt* to the model assigned to *role*, with automatic fallback."""
        models_cfg = self._config["models"]
        if role not in models_cfg:
            raise ValueError(f"Unknown role: {role}")

        cfg = models_cfg[role]
        tokens = max_tokens or cfg.get("max_tokens", 4096)
        temp = temperature if temperature is not None else cfg.get("temperature")

        api_type = cfg.get("api_type", "chat")

        try:
            return self._dispatch(cfg["provider"], cfg["model"], prompt, tokens, temp, api_type)
        except Exception:
            logger.warning(
                "Primary provider failed for role=%s, falling back", role, exc_info=True,
            )
            fb = self._config["fallback"]
            return self._dispatch(
                fb["provider"],
                fb["model"],
                prompt,
                fb.get("max_tokens", 4096),
                temp,
                fb.get("api_type", "chat"),
            )

    # -- internal dispatch -------------------------------------------------

    def _dispatch(
        self,
        provider: str,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: float | None = None,
        api_type: str = "chat",
    ) -> str:
        logger.info("[ModelRouter] provider=%s model=%s max_tokens=%d api_type=%s", provider, model, max_tokens, api_type)
        if provider == "anthropic":
            return self._call_anthropic(model, prompt, max_tokens, temperature)
        if provider == "openai":
            return self._call_openai(model, prompt, max_tokens, temperature, api_type)
        if provider == "replicate":
            return self._call_replicate(model, prompt, max_tokens)
        raise ValueError(f"Unknown provider: {provider}")

    def _call_anthropic(
        self,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: float | None = None,
    ) -> str:
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if temperature is not None:
            kwargs["temperature"] = temperature
        response = self.anthropic_client.messages.create(**kwargs)
        return response.content[0].text

    def _call_openai(
        self,
        model: str,
        prompt: str,
        max_tokens: int,
        temperature: float | None = None,
        api_type: str = "chat",
    ) -> str:
        if api_type == "completions":
            kwargs = {
                "model": model,
                "prompt": prompt,
                "max_tokens": max_tokens,
            }
            if temperature is not None:
                kwargs["temperature"] = temperature
            response = self.openai_client.completions.create(**kwargs)
            return response.choices[0].text
        else:
            kwargs = {
                "model": model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }
            if temperature is not None:
                kwargs["temperature"] = temperature
            response = self.openai_client.chat.completions.create(**kwargs)
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
