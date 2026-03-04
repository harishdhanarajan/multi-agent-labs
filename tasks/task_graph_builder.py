"""Task Graph Builder — builds a dependency graph and topological execution order."""

import json
import logging
from collections import deque
from pathlib import Path

from tasks.task_models import TaskGraph, TaskQueue

logger = logging.getLogger(__name__)

_TASK_QUEUE_PATH = Path(__file__).resolve().parent.parent / "tasks" / "task_queue.json"
_TASK_GRAPH_PATH = Path(__file__).resolve().parent.parent / "tasks" / "task_graph.json"


class TaskGraphBuilder:
    """Reads task_queue.json, builds a DAG, and produces an execution order."""

    def build(self, queue: TaskQueue | None = None) -> TaskGraph:
        """Build graph from *queue* or from the persisted task_queue.json."""
        if queue is None:
            raw = json.loads(_TASK_QUEUE_PATH.read_text(encoding="utf-8"))
            queue = TaskQueue(**raw)

        # Build adjacency list: task_id -> list of tasks that depend on it
        adjacency: dict[int, list[int]] = {}
        in_degree: dict[int, int] = {}

        for task in queue.tasks:
            tid = task.task_id
            adjacency.setdefault(tid, [])
            in_degree.setdefault(tid, 0)

        for task in queue.tasks:
            for dep in task.dependencies:
                adjacency.setdefault(dep, []).append(task.task_id)
                in_degree[task.task_id] = in_degree.get(task.task_id, 0) + 1

        # Kahn's algorithm for topological sort
        order: list[int] = []
        ready: deque[int] = deque(
            tid for tid, deg in in_degree.items() if deg == 0
        )

        while ready:
            tid = ready.popleft()
            order.append(tid)
            for neighbour in adjacency.get(tid, []):
                in_degree[neighbour] -= 1
                if in_degree[neighbour] == 0:
                    ready.append(neighbour)

        if len(order) != len(queue.tasks):
            logger.error("Cycle detected in task dependencies!")
            raise ValueError("Task dependency graph contains a cycle")

        graph = TaskGraph(adjacency=adjacency, execution_order=order)

        # Persist
        _TASK_GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
        _TASK_GRAPH_PATH.write_text(graph.model_dump_json(indent=2), encoding="utf-8")
        logger.info("Task graph saved with execution order: %s", order)

        return graph
