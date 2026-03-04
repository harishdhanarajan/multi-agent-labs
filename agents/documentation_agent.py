"""Documentation Agent — generates README and docstrings for workspace code."""

import logging

from agents.base_agent import BaseAgent
from execution.patch_engine import PatchEngine
from tasks.task_models import PatchSet
from tools.workspace_loader import WorkspaceLoader

logger = logging.getLogger(__name__)


class DocumentationAgent(BaseAgent):
    """Generates documentation based on the current workspace code."""

    @property
    def role(self) -> str:
        return "documenter"

    def generate_docs(self) -> PatchSet:
        workspace_context = WorkspaceLoader().format_for_prompt()

        prompt = f"""You are a technical documentation writer.

Based on the code below, generate a README.md that describes:
- What the project does
- How to use it
- Module/function documentation

Output the file in this exact format:

FILE: workspace/README.md
```markdown
<documentation here>
```

Current workspace files:
{workspace_context}
"""

        response = self.call_llm(prompt)
        doc_patches = PatchEngine.parse_patches(response)

        logger.info("Documenter produced %d file(s)", len(doc_patches.patches))
        return doc_patches
