"""Test Runner — executes pytest on workspace test files."""

import logging
import re
import subprocess
from pathlib import Path

from tasks.task_models import TestResult

logger = logging.getLogger(__name__)

_WORKSPACE_DIR = Path(__file__).resolve().parent.parent / "workspace"


class TestRunner:
    """Runs pytest against the workspace and parses results."""

    def __init__(self, workspace_dir: Path | str | None = None):
        self.workspace_dir = Path(workspace_dir) if workspace_dir else _WORKSPACE_DIR

    def run(self, timeout: int = 60) -> TestResult:
        """Execute pytest on the workspace directory. Returns TestResult."""
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", str(self.workspace_dir), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.workspace_dir.parent),
            )
            output = result.stdout + "\n" + result.stderr
        except subprocess.TimeoutExpired:
            logger.error("pytest timed out after %ds", timeout)
            return TestResult(passed=False, output=f"pytest timed out after {timeout}s")
        except FileNotFoundError:
            logger.error("pytest not found")
            return TestResult(passed=False, output="pytest executable not found")

        passed, total, failures = self._parse_summary(output)

        return TestResult(
            passed=(failures == 0 and total > 0),
            total=total,
            failures=failures,
            output=output,
        )

    @staticmethod
    def _parse_summary(output: str) -> tuple[int, int, int]:
        """Extract pass/fail counts from pytest output."""
        # Match lines like "5 passed", "2 failed, 3 passed"
        passed = 0
        failed = 0

        m = re.search(r"(\d+) passed", output)
        if m:
            passed = int(m.group(1))

        m = re.search(r"(\d+) failed", output)
        if m:
            failed = int(m.group(1))

        total = passed + failed
        return passed, total, failed
