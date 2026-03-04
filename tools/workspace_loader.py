"""Workspace Loader — reads workspace files for inclusion in LLM prompts."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "workspace"

# Only load files with these extensions
_ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css",
    ".json", ".yaml", ".yml", ".toml", ".cfg", ".ini",
    ".md", ".txt", ".rst", ".sh", ".bat",
}

_MAX_FILE_SIZE = 50_000  # bytes


class WorkspaceLoader:
    """Loads workspace files so agents can see the current codebase."""

    def __init__(self, workspace_dir: Path | str | None = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else _WORKSPACE_DIR

    def load_all(self) -> dict[str, str]:
        """Return {relative_path: file_content} for every eligible workspace file."""
        files: dict[str, str] = {}
        if not self.workspace_dir.exists():
            logger.warning("Workspace directory does not exist: %s", self.workspace_dir)
            return files

        for path in sorted(self.workspace_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in _ALLOWED_EXTENSIONS:
                continue
            if path.stat().st_size > _MAX_FILE_SIZE:
                logger.info("Skipping large file: %s", path)
                continue
            try:
                rel = path.relative_to(self.workspace_dir).as_posix()
                files[rel] = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                logger.warning("Failed to read %s", path, exc_info=True)
        return files

    def format_for_prompt(self) -> str:
        """Return a formatted string of all workspace files for LLM prompts."""
        files = self.load_all()
        if not files:
            return "(workspace is empty)"

        parts: list[str] = []
        for rel_path, content in files.items():
            parts.append(f"FILE: {rel_path}\n```\n{content}\n```")
        return "\n\n".join(parts)
