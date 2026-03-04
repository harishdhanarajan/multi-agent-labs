"""Reviewer Agent — reviews code patches for correctness and quality."""

import json
import logging
import re

from agents.base_agent import BaseAgent
from tasks.task_models import PatchSet, ReviewResult, ReviewVerdict, Task

logger = logging.getLogger(__name__)


class ReviewerAgent(BaseAgent):
    """Reviews code patches and returns APPROVED or REVISE."""

    @property
    def role(self) -> str:
        return "reviewer"

    def review(self, task: Task, patch_set: PatchSet) -> ReviewResult:
        patches_text = "\n\n".join(
            f"FILE: {p.file_path}\n```\n{p.content}\n```" for p in patch_set.patches
        )

        prompt = f"""You are a senior code reviewer.

Review the following code patches against the task description.

Return ONLY a JSON object with:
- "verdict": "APPROVED" or "REVISE"
- "comments": explanation of issues (empty string if approved)

Task: {task.task}

Patches:
{patches_text}
"""

        response = self.call_llm(prompt)

        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except json.JSONDecodeError:
                    logger.warning("Reviewer returned unparseable response, defaulting to APPROVED")
                    return ReviewResult(verdict=ReviewVerdict.APPROVED, comments="")
            else:
                logger.warning("Reviewer returned unparseable response, defaulting to APPROVED")
                return ReviewResult(verdict=ReviewVerdict.APPROVED, comments="")

        verdict_str = data.get("verdict", "APPROVED").upper()
        verdict = ReviewVerdict.REVISE if verdict_str == "REVISE" else ReviewVerdict.APPROVED
        return ReviewResult(verdict=verdict, comments=data.get("comments", ""))
