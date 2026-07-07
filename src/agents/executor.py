import json
import subprocess
import sys
from pathlib import Path

from src.model.schema import State, ExecutorResult

from langsmith import traceable, get_current_run_tree


def executor_node(state: State) -> State:

    print("EXECUTOR AGENT IN PROGRESS...")

    if state.project is None:
        raise ValueError("[EXECUTOR] Project has not been generated yet")

    entry_file_path = state.project.entry_point

    file_input_list = state.project.file_inputs

    file_input_data = ""

    for input_data in file_input_list:
        file_input_data += input_data + "\n"

    retry_count = getattr(state, "retry_fix", 0)

    result = execute_and_diagnose(entry_file_path, file_input_data, retry_count=retry_count)

    state.executor = ExecutorResult(
        task=state.user_input,
        file_path=entry_file_path,
        **result
    )

    return state


@traceable(run_type="tool", name="run_subprocess")
def run_subprocess(path: Path, file_input_data: str, timeout: int) -> dict:
    """Spawn the subprocess and capture raw execution output. Raises on timeout."""
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=path.parent,
        input=file_input_data,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.returncode,
    }


@traceable(run_type="parser", name="diagnose_error")
def diagnose_error(exec_result: dict) -> dict:
    """Turn raw subprocess output into a success/failure verdict + error summary."""
    success = exec_result["exit_code"] == 0
    stderr_lines = [l for l in exec_result["stderr"].strip().splitlines() if l.strip()]

    error_summary = None
    if not success:
        last_line = stderr_lines[-1] if stderr_lines else "Unknown error"
        print(f"ERROR: {last_line}")
        if "EOFError" in exec_result["stderr"]:
            error_summary = "Code called input() or similar blocking stdin read — not allowed in subprocess execution. Remove all input() calls and use hardcoded values or argparse instead."
            print(f"ERROR: {error_summary}")
        else:
            error_summary = last_line
            print(f"ERROR: {error_summary}")

    return {**exec_result, "success": success, "error_summary": error_summary}


@traceable(name="execute_and_diagnose")
def execute_and_diagnose(file_path: str, file_input_data: str, timeout: int = 7, retry_count: int = 0) -> dict:
    """Run a Python file and return execution results + error context for the coder agent to fix."""

    run = get_current_run_tree()
    if run:
        run.metadata["retry_count"] = retry_count

    path = Path(file_path).resolve()

    if not path.exists():
        print(f"Path does not exist: {path}")

        return {
            "success": False,
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "error_summary": f"File not found: {path}"
        }

    try:
        exec_result = run_subprocess(path, file_input_data, timeout)
        return diagnose_error(exec_result)

    except subprocess.TimeoutExpired as e:
        error_summary = f"Execution timed out after {timeout}s — check for infinite loops or blocking calls."
        print(f"ERROR: {error_summary}")

        return {
            "success": False,
            "stdout": e.stdout or "",
            "stderr": e.stderr or "",
            "exit_code": -1,
            "error_summary": error_summary
        }

    except Exception as e:
        error_summary = f"Executor crashed: {e}"
        print(f"ERROR: {error_summary}")

        return {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "error_summary": error_summary
        }

def route_to_critic(state: State) -> str:
    """Route to CRITIC if the executor result shows errors, failures, or warnings."""

    if state.executor is None:
        raise ValueError("[EXECUTOR] Executor is None")

    if state.executor.success:
        return "DONE"

    return "CRITIC"