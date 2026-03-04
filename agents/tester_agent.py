"""Tester Agent — generates pytest test files for code changes."""

import logging

from agents.base_agent import BaseAgent
from execution.patch_engine import PatchEngine
from tasks.task_models import PatchSet, Task

logger = logging.getLogger(__name__)


class TesterAgent(BaseAgent):
    """Generates pytest tests for a given task and its code patches."""

    @property
    def role(self) -> str:
        return "tester"

    def generate_tests(self, task: Task, code_patches: PatchSet) -> PatchSet:
        code_text = "\n\n".join(
            f"FILE: {p.file_path}\n```\n{p.content}\n```" for p in code_patches.patches
        )

        prompt = f"""You are a test engineer.

Write pytest test files for the code below.

For EACH test file, output it in this exact format:

FILE: workspace/test_filename.py
```python
<test code here>
```

Only write test files inside the workspace/ directory.
Use standard pytest conventions. Import from the modules being tested.

Task: {task.task}

Code:
{code_text}
"""

        response = self.call_llm(prompt)
        test_patches = PatchEngine.parse_patches(response)

        logger.info(
            "Tester produced %d test file(s) for task %d",
            len(test_patches.patches),
            task.task_id,
        )
        return test_patches
