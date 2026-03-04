"""Pydantic models shared across all agents and components."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Task(BaseModel):
    """A single engineering task produced by the planner."""

    task_id: int
    task: str
    dependencies: list[int] = Field(default_factory=list)
    status: str = "pending"  # pending | in_progress | done | failed


class TaskQueue(BaseModel):
    """Ordered list of tasks persisted to task_queue.json."""

    tasks: list[Task] = Field(default_factory=list)


class TaskGraph(BaseModel):
    """Dependency graph produced by the task graph builder."""

    adjacency: dict[int, list[int]] = Field(default_factory=dict)
    execution_order: list[int] = Field(default_factory=list)


class FilePatch(BaseModel):
    """A single file to create or overwrite."""

    file_path: str
    content: str


class PatchSet(BaseModel):
    """Collection of file patches returned by coder / debugger / documenter."""

    patches: list[FilePatch] = Field(default_factory=list)


class ReviewVerdict(str, Enum):
    APPROVED = "APPROVED"
    REVISE = "REVISE"


class ReviewResult(BaseModel):
    """Output of the reviewer agent."""

    verdict: ReviewVerdict
    comments: str = ""


class TestResult(BaseModel):
    """Output of the test runner."""

    passed: bool
    total: int = 0
    failures: int = 0
    output: str = ""


class DebugResult(BaseModel):
    """Output of the debugger agent."""

    diagnosis: str
    fix: Optional[PatchSet] = None
