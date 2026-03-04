"""Patch Engine — parses LLM code output and safely writes files to workspace."""

import logging
import re
from pathlib import Path

import yaml

from tasks.task_models import FilePatch, PatchSet

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "model_config.yaml"
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_safety_config() -> dict:
    with open(_CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg.get("safety", {})


class PatchEngine:
    """Extracts file patches from LLM output and writes them to disk."""

    def __init__(self):
        safety = _load_safety_config()
        self._protected: list[str] = safety.get("protected_paths", [])
        self._allowed: list[str] = safety.get("allowed_paths", ["workspace/"])

    # -- parsing -----------------------------------------------------------

    @staticmethod
    def parse_patches(llm_output: str) -> PatchSet:
        """Extract ``FILE: path`` + fenced code blocks from raw LLM text.

        Expected format in the LLM response::

            FILE: path/to/file.py
            ```python
            <code>
            ```
        """
        pattern = r"FILE:\s*(\S+)\s*\n```[^\n]*\n(.*?)```"
        matches = re.findall(pattern, llm_output, re.DOTALL)

        patches = [FilePatch(file_path=m[0], content=m[1]) for m in matches]
        return PatchSet(patches=patches)

    # -- application -------------------------------------------------------

    def apply_patches(self, patch_set: PatchSet) -> list[str]:
        """Write each patch to disk. Returns list of written file paths."""
        written: list[str] = []
        for patch in patch_set.patches:
            if not self._is_safe_path(patch.file_path):
                logger.error("Blocked write to protected path: %s", patch.file_path)
                continue

            target = _PROJECT_ROOT / patch.file_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(patch.content, encoding="utf-8")
            logger.info("Wrote %s", target)
            written.append(patch.file_path)
        return written

    # -- validation --------------------------------------------------------

    @staticmethod
    def validate_syntax(patch: FilePatch) -> tuple[bool, str]:
        """Compile-check Python files. Returns (ok, error_message)."""
        if not patch.file_path.endswith(".py"):
            return True, ""
        try:
            compile(patch.content, patch.file_path, "exec")
            return True, ""
        except SyntaxError as exc:
            return False, f"SyntaxError at line {exc.lineno}: {exc.msg}"

    # -- safety ------------------------------------------------------------

    def _is_safe_path(self, file_path: str) -> bool:
        """Return True if *file_path* is inside an allowed directory and not protected."""
        normalized = file_path.replace("\\", "/")
        for protected in self._protected:
            if normalized.startswith(protected):
                return False
        for allowed in self._allowed:
            if normalized.startswith(allowed):
                return True
        # Deny by default if not in an allowed path
        return False
