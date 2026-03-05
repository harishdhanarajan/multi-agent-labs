"""Orchestrator — main pipeline that coordinates all agents end-to-end."""

import logging
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from agents.coder_agent import CoderAgent
from agents.debugger_agent import DebuggerAgent
from agents.documentation_agent import DocumentationAgent
from agents.planner_agent import PlannerAgent
from agents.reviewer_agent import ReviewerAgent
from agents.tester_agent import TesterAgent
from execution.patch_engine import PatchEngine
from orchestrator.intent_classifier import (
    INTENT_AMBIGUOUS,
    INTENT_BUILD,
    INTENT_QUESTION,
    IntentClassifier,
)
from orchestrator.model_router import ModelRouter
from orchestrator.qa_responder import QAResponder
from tasks.task_graph_builder import TaskGraphBuilder
from tasks.task_models import ReviewVerdict
from tools.test_runner import TestRunner

console = Console(force_terminal=True)
logger = logging.getLogger(__name__)

MAX_REVIEW_ROUNDS = 3
MAX_DEBUG_ROUNDS = 3


def _fmt_elapsed(seconds: float) -> str:
    """Return a compact human-readable elapsed time string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes, secs = divmod(seconds, 60)
    return f"{int(minutes)}m {secs:.0f}s"


GENERATED_TEST_MARKER = "# GENERATED_BY_MULTI_AGENT_TESTER"
_WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "workspace"


def _tag_generated_tests(test_patches) -> None:
    """Mark tester-generated files so stale ones can be cleaned up safely."""
    for patch in test_patches.patches:
        if patch.file_path.startswith("workspace/test_") and patch.file_path.endswith(".py"):
            if not patch.content.lstrip().startswith(GENERATED_TEST_MARKER):
                patch.content = f"{GENERATED_TEST_MARKER}\n{patch.content}"


def _cleanup_stale_generated_tests(incoming_paths: set[str]) -> None:
    """Delete old auto-generated test files that are not in the incoming patch set."""
    if not _WORKSPACE_DIR.exists():
        return
    for path in _WORKSPACE_DIR.glob("test_*.py"):
        rel_path = f"workspace/{path.name}"
        if rel_path in incoming_paths:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if content.lstrip().startswith(GENERATED_TEST_MARKER):
            path.unlink(missing_ok=True)
            logger.info("Removed stale generated test file: %s", rel_path)


def run_pipeline(user_request: str) -> None:
    """Execute the full multi-agent pipeline for *user_request*."""

    pipeline_start = time.monotonic()

    console.print(Panel(f"[bold cyan]Request:[/] {user_request}", title="Multi-Agent Pipeline"))

    router = ModelRouter()

    intent = IntentClassifier(router).classify(user_request)
    if intent == INTENT_QUESTION:
        answer = QAResponder(router).answer(user_request)
        console.print(Panel(answer or "(No answer returned)", title="Q&A Response"))
        return
    if intent == INTENT_AMBIGUOUS:
        console.print("[dim]Intent ambiguous -- proceeding with full pipeline.[/]")

    patch_engine = PatchEngine()

    # ── Phase 1: Planning ─────────────────────────────────────────────
    t0 = time.monotonic()
    console.print("\n[bold yellow]Phase 1: Planning[/]")
    planner = PlannerAgent(router)
    queue = planner.create_plan(user_request)
    if queue is None or not queue.tasks:
        console.print("[red]Planner failed to produce tasks. Aborting.[/]")
        return
    for t in queue.tasks:
        console.print(f"  Task {t.task_id}: {t.task}")
    console.print(f"[dim]  Planning done in {_fmt_elapsed(time.monotonic() - t0)}[/]")

    # ── Phase 2: Task Graph ───────────────────────────────────────────
    graph_builder = TaskGraphBuilder()
    graph = graph_builder.build(queue)

    # ── Phase 3-6: Per-task loop ──────────────────────────────────────
    coder = CoderAgent(router)
    reviewer = ReviewerAgent(router)
    tester = TesterAgent(router)
    debugger = DebuggerAgent(router)
    test_runner = TestRunner()

    task_lookup = {t.task_id: t for t in queue.tasks}

    for task_id in graph.execution_order:
        task = task_lookup[task_id]
        task_start = time.monotonic()
        console.print(f"\n[bold green]--- Task {task.task_id}: {task.task} ---[/]")

        # ── Coding + Review loop ──────────────────────────────────────
        console.print("  [cyan]Coding...[/]")
        code_patches = coder.generate_code(task)
        if not code_patches.patches:
            console.print("  [red]No patches produced, skipping.[/]")
            task.status = "failed"
            continue

        for review_round in range(1, MAX_REVIEW_ROUNDS + 1):
            review = reviewer.review(task, code_patches)
            verdict = review.verdict.value
            if review.verdict == ReviewVerdict.APPROVED:
                console.print(f"  [green]Review: {verdict}[/]")
                break
            console.print(f"  [yellow]Review: {verdict}[/]")
            if review.comments:
                console.print(f"    {review.comments[:120]}")
            if review_round < MAX_REVIEW_ROUNDS:
                console.print("  [cyan]Revising...[/]")
                code_patches = coder.generate_code(task)
        else:
            console.print("  [yellow]Max review rounds reached, proceeding.[/]")

        # ── Apply patches ─────────────────────────────────────────────
        written = patch_engine.apply_patches(code_patches)
        console.print(f"  Wrote {len(written)} file(s)")

        # ── Testing + Debug loop ──────────────────────────────────────
        console.print("  [cyan]Testing...[/]")
        test_patches = tester.generate_tests(task, code_patches)
        if test_patches.patches:
            _tag_generated_tests(test_patches)
            incoming_test_paths = {p.file_path for p in test_patches.patches}
            _cleanup_stale_generated_tests(incoming_test_paths)
            patch_engine.apply_patches(test_patches)

        for debug_round in range(1, MAX_DEBUG_ROUNDS + 1):
            test_result = test_runner.run()
            if test_result.passed:
                console.print(f"  [green]Tests passed ({test_result.total} total)[/]")
                break

            console.print(
                f"  [red]Tests: {test_result.failures}/{test_result.total} failed[/]"
            )
            if debug_round < MAX_DEBUG_ROUNDS:
                console.print("  [cyan]Debugging...[/]")
                debug_result = debugger.debug(task, code_patches, test_result.output)
                if debug_result.fix and debug_result.fix.patches:
                    patch_engine.apply_patches(debug_result.fix)
                    code_patches = debug_result.fix
                else:
                    console.print("  [yellow]No fix produced, moving on.[/]")
                    break
        else:
            console.print("  [yellow]Max debug rounds reached.[/]")

        task.status = "done"
        console.print(f"  [dim]Task done in {_fmt_elapsed(time.monotonic() - task_start)}[/]")

    # ── Phase 7: Documentation ────────────────────────────────────────
    t0 = time.monotonic()
    console.print("\n[bold yellow]Generating docs...[/]")
    documenter = DocumentationAgent(router)
    doc_patches = documenter.generate_docs()
    if doc_patches.patches:
        patch_engine.apply_patches(doc_patches)
        console.print(f"  Documentation generated in {_fmt_elapsed(time.monotonic() - t0)}")
    else:
        console.print("  [yellow]No documentation produced.[/]")

    # ── Done ──────────────────────────────────────────────────────────
    total = _fmt_elapsed(time.monotonic() - pipeline_start)
    console.print(Panel(f"[bold green]Pipeline complete[/] in {total}", title="Done"))


def main():
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    if len(sys.argv) < 2:
        console.print("[red]Usage: python -m orchestrator.orchestrator \"<request>\"[/]")
        sys.exit(1)

    request = " ".join(sys.argv[1:])
    run_pipeline(request)


if __name__ == "__main__":
    main()
