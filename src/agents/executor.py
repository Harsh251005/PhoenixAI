import subprocess
import sys
from pathlib import Path

from src.model.schema import State, ExecutorResult


def executor_node(state: State) -> State:

    print("EXECUTOR AGENT IN PROGRESS...")

    file_path = state.project.file.file_path

    file_input_list = state.project.file.file_inputs

    file_input_data = ""

    for input_data in file_input_list:
        file_input_data += input_data + "\n"

    print(f"FILE_INPUT_LIST: {file_input_list}\nFILE_INPUT_DATA: {file_input_data}\n")

    result = execute_and_diagnose(file_path, file_input_data)

    state.executor = ExecutorResult(
        task=state.user_input,
        code=state.project.file.file_content,
        file_path=file_path,
        retry_count=getattr(state.executor, "retry_count", 0),
        **result
    )

    print(f"\nEXECUTOR STATE:\n{state.executor}\n")

    return state

def route_after_execution(state: State) -> str:
    if state.executor.success:
        print("\nTHE CODE WAS SUCCESSFULLY GENERATED AND EXECUTED\n")
        return "done"

    if state.executor.retry_count >= 3:
        print(f"\nTHE CODER AGENT COULD NOT SOLVE THE ERROR:{state.executor.error_summary}\n")
        return "give_up"

    print("\nFOUND ERROR!\nREDIRECTING TO CODER AGENT\n")

    return "retry_coder"

def increment_retry(state: State):

    new_executor = state.executor.model_copy(
        update={
            "retry_count": state.executor.retry_count + 1
        }
    )

    print(f"\n{'-' * 100}\n")

    return {
        "executor": new_executor
    }


def execute_and_diagnose(file_path: str, file_input_data, timeout: int = 30) -> dict:
    """Run a Python file and return execution results + error context for the coder agent to fix."""
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
        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=path.parent,
            input=file_input_data,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        success = result.returncode == 0
        stderr_lines = [l for l in result.stderr.strip().splitlines() if l.strip()]

        error_summary = None
        if not success:
            last_line = stderr_lines[-1] if stderr_lines else "Unknown error"
            print(f"ERROR: {last_line}")
            if "EOFError" in result.stderr:
                error_summary = "Code called input() or similar blocking stdin read — not allowed in subprocess execution. Remove all input() calls and use hardcoded values or argparse instead."
                print(f"ERROR: {error_summary}")
            else:
                error_summary = last_line
                print(f"ERROR: {error_summary}")

        return {
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
            "error_summary": error_summary,
        }

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
