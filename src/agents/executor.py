import subprocess
import sys
from pathlib import Path

from src.model.schema import State, ExecutorResult


def executor_node(state: State) -> State:

    print("EXECUTOR AGENT IN PROGRESS...")

    file_path = state.project.file.file_path

    result = execute_and_diagnose(file_path)

    state.executor = ExecutorResult(
        task=state.user_input,
        code=state.project.file.file_content,
        file_path=file_path,
        **result
    )

    return state



def execute_and_diagnose(file_path: str, timeout: int = 30) -> dict:
    """Run a Python file and return execution results + error context for the coder agent to fix."""
    path = Path(file_path).resolve()

    if not path.exists():
        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "error_summary": f"File not found: {path}",
        }

    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=path.parent,
            capture_output=True,
            text=True,
            timeout=timeout,
            stdin=subprocess.DEVNULL
        )
        success = result.returncode == 0
        stderr_lines = [l for l in result.stderr.strip().splitlines() if l.strip()]

        error_summary = None
        if not success:
            last_line = stderr_lines[-1] if stderr_lines else "Unknown error"
            if "EOFError" in result.stderr:
                error_summary = "Code called input() or similar blocking stdin read — not allowed in subprocess execution. Remove all input() calls and use hardcoded values or argparse instead."
            else:
                error_summary = last_line

        return {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "error_summary": error_summary,
        }

    except subprocess.TimeoutExpired as e:
        return {
            "success": False,
            "stdout": e.stdout or "",
            "stderr": e.stderr or "",
            "exit_code": -1,
            "error_summary": f"Execution timed out after {timeout}s — check for infinite loops or blocking calls.",
        }

    except Exception as e:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "error_summary": f"Executor crashed: {e}",
        }
