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
        module_names = [
            p.file_path.split("/")[-1].rsplit(".", 1)[0]
            for p in code_patches.patches
            if p.file_path.startswith("workspace/")
            and p.file_path.endswith(".py")
            and not p.file_path.split("/")[-1].startswith("test_")
        ]
        unique_modules = sorted(set(module_names))
        expected_tests = [f"workspace/test_{name}.py" for name in unique_modules]
        expected_list = "\n".join(f"- {path}" for path in expected_tests) or "- workspace/test_generated.py"

        prompt = f"""You are a test engineer.

Write pytest test files for the code below.

Generate exactly one test file per module listed below.
Do not create alternate variants like *_context, *_upload_file, *_defaults, *_env_vars.
Only use these test file paths:
{expected_list}

For each file, output in this exact format:

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
        if expected_tests:
            allowed = set(expected_tests)
            test_patches.patches = [p for p in test_patches.patches if p.file_path in allowed]

        logger.info(
            "Tester produced %d test file(s) for task %d",
            len(test_patches.patches),
            task.task_id,
        )
        return test_patches
