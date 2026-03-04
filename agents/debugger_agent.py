"""Debugger Agent — diagnoses test failures and proposes fixes."""

import logging

from agents.base_agent import BaseAgent
from execution.patch_engine import PatchEngine
from tasks.task_models import DebugResult, PatchSet, Task

logger = logging.getLogger(__name__)


class DebuggerAgent(BaseAgent):
    """Analyzes failing tests and produces fix patches."""

    @property
    def role(self) -> str:
        return "debugger"

    def debug(self, task: Task, code_patches: PatchSet, test_output: str) -> DebugResult:
        code_text = "\n\n".join(
            f"FILE: {p.file_path}\n```\n{p.content}\n```" for p in code_patches.patches
        )

        prompt = f"""You are a debugging expert.

The following tests failed. Diagnose the root cause and provide fixed code.

Return your response in TWO parts:

1. DIAGNOSIS: A brief explanation of the root cause.

2. FIXED FILES: For each file that needs fixing, use this exact format:

FILE: workspace/filename.py
```python
<fixed code>
```

Task: {task.task}

Code:
{code_text}

Test output:
{test_output}
"""

        response = self.call_llm(prompt)

        # Extract diagnosis (text before the first FILE: block)
        diagnosis = response.split("FILE:")[0].strip()
        if "DIAGNOSIS:" in diagnosis:
            diagnosis = diagnosis.split("DIAGNOSIS:", 1)[1].strip()

        # Extract fix patches
        fix_patches = PatchEngine.parse_patches(response)

        logger.info(
            "Debugger produced %d fix(es) for task %d",
            len(fix_patches.patches),
            task.task_id,
        )

        return DebugResult(
            diagnosis=diagnosis,
            fix=fix_patches if fix_patches.patches else None,
        )
