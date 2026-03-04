"""Coder Agent — generates code patches for a given task."""

import logging

from agents.base_agent import BaseAgent
from execution.patch_engine import PatchEngine
from tasks.task_models import PatchSet, Task
from tools.workspace_loader import WorkspaceLoader

logger = logging.getLogger(__name__)


class CoderAgent(BaseAgent):
    """Writes code to fulfil a single engineering task."""

    @property
    def role(self) -> str:
        return "coder"

    def generate_code(self, task: Task) -> PatchSet:
        workspace_context = WorkspaceLoader().format_for_prompt()

        prompt = f"""You are an expert software engineer.

Implement the following task by producing code files.

For EACH file, output it in this exact format:

FILE: workspace/filename.py
```python
<code here>
```

Only write files inside the workspace/ directory.

Current workspace files:
{workspace_context}

Task:
{task.task}
"""

        response = self.call_llm(prompt)
        patch_set = PatchEngine.parse_patches(response)

        # Validate syntax of Python patches
        for patch in patch_set.patches:
            ok, err = PatchEngine.validate_syntax(patch)
            if not ok:
                logger.warning("Syntax error in %s: %s", patch.file_path, err)

        logger.info("Coder produced %d file(s) for task %d", len(patch_set.patches), task.task_id)
        return patch_set
