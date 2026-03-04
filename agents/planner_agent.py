"""Planner Agent — breaks a user request into an ordered task list."""

import json
import logging
import re
from pathlib import Path

from agents.base_agent import BaseAgent
from tasks.task_models import Task, TaskQueue
from tools.workspace_loader import WorkspaceLoader

logger = logging.getLogger(__name__)

_TASK_QUEUE_PATH = Path(__file__).resolve().parent.parent / "tasks" / "task_queue.json"


class PlannerAgent(BaseAgent):
    """Generates an engineering task plan from a natural-language request."""

    @property
    def role(self) -> str:
        return "planner"

    def create_plan(self, user_request: str) -> TaskQueue | None:
        workspace_context = WorkspaceLoader().format_for_prompt()

        prompt = f"""You are a software planning agent.

Break the following request into clear, ordered engineering tasks.

Return ONLY a JSON list. Each item must have:
- "task_id": integer starting at 1
- "task": short description of the task
- "dependencies": list of task_id integers this task depends on (use [] if none)

Example:
[
  {{"task_id": 1, "task": "Create utils module", "dependencies": []}},
  {{"task_id": 2, "task": "Add main logic using utils", "dependencies": [1]}}
]

Current workspace files:
{workspace_context}

User request:
{user_request}
"""

        response = self.call_llm(prompt)

        try:
            raw = json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON array from the response
            match = re.search(r"\[.*\]", response, re.DOTALL)
            if match:
                try:
                    raw = json.loads(match.group())
                except json.JSONDecodeError:
                    logger.error("Planner returned invalid JSON:\n%s", response)
                    return None
            else:
                logger.error("Planner returned invalid JSON:\n%s", response)
                return None

        tasks = [Task(**item) for item in raw]
        queue = TaskQueue(tasks=tasks)

        # Persist to disk
        _TASK_QUEUE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _TASK_QUEUE_PATH.write_text(queue.model_dump_json(indent=2), encoding="utf-8")
        logger.info("Saved %d tasks to %s", len(tasks), _TASK_QUEUE_PATH)

        return queue
