import subprocess
from pathlib import Path

from langsmith import get_current_run_tree, traceable

from src.config.settings import settings
from src.model.schema import State, ExecutorResult, TerminalCommand


@traceable(run_type="tool", name="executor_agent")
def executor_node(state: State) -> State:
    """Run generated commands in a constrained, network-disabled Docker container."""
    print("EXECUTOR AGENT IN PROGRESS...")

    if state.project is None:
        raise ValueError("[EXECUTOR] Project has not been generated yet")

    project_dir = _project_directory(state.project.project_name)
    if not project_dir.is_dir():
        raise ValueError(f"[EXECUTOR] Generated project directory does not exist: {project_dir}")

    commands = _commands_with_inputs(state.project.terminal_commands, state.project.file_inputs)
    if not commands:
        result = {
            "success": False,
            "stdout": "",
            "stderr": "No terminal commands were provided by the coder.",
            "exit_code": -1,
            "error_summary": "No terminal commands were provided.",
        }
    else:
        execution_results = []
        retry_count = getattr(state, "retry_fix", 0)
        for command in commands:
            result = execute_and_diagnose(command, project_dir, retry_count=retry_count)
            execution_results.append(result)
            if not result["success"]:
                break
        result = execution_results[-1]

    state.executor = ExecutorResult(task=state.user_input, file_path=str(project_dir), **result)
    return state


def _project_directory(project_name: str) -> Path:
    root = settings.GENERATED_PROJECTS_DIR.resolve()
    project_dir = (root / project_name).resolve()
    if not project_dir.is_relative_to(root):
        raise ValueError(f"[EXECUTOR] Unsafe project name: {project_name!r}")
    return project_dir


def _commands_with_inputs(commands: list[TerminalCommand], inputs: list[str]) -> list[TerminalCommand]:
    if not inputs or not commands or commands[0].stdin is not None:
        return commands
    updated = list(commands)
    updated[0] = commands[0].model_copy(update={"stdin": "\n".join(inputs) + "\n"})
    return updated


def _docker_args(command: TerminalCommand, cwd: Path, timeout: int) -> list[str]:
    image = settings.DOCKER_EXECUTOR_IMAGE
    args = [
        "docker", "run", "--rm", "--network", settings.DOCKER_NETWORK,
        "--memory", settings.DOCKER_MEMORY, "--cpus", settings.DOCKER_CPUS,
        "--pids-limit", str(settings.DOCKER_PIDS_LIMIT),
        "--read-only", "--cap-drop=ALL", "--security-opt", "no-new-privileges",
        # The generated project is mounted read-only. Use Docker's automatic
        # user when available; a fixed UID can make host-created files
        # unreadable on SELinux-enabled systems (e.g. Fedora/RHEL).
        "-v", f"{cwd}:/app:ro,Z", "-w", "/app", image,
    ]
    return args + command.command


@traceable(run_type="tool", name="run_docker")
def run_docker(command: TerminalCommand, cwd: Path, timeout: int) -> dict:
    kwargs = {
        "args": _docker_args(command, cwd, timeout),
        "capture_output": True,
        "text": True,
        "timeout": timeout,
    }
    if command.stdin is not None:
        kwargs["input"] = command.stdin
    result = subprocess.run(**kwargs)
    return {"stdout": result.stdout, "stderr": result.stderr, "exit_code": result.returncode}


@traceable(run_type="parser", name="diagnose_error")
def diagnose_error(exec_result: dict) -> dict:
    stderr = exec_result.get("stderr", "")
    stderr_lines = [line for line in stderr.splitlines() if line.strip()]
    has_traceback = "traceback (most recent call last)" in stderr.lower()
    has_exception = any("exception" in line.lower() or "error:" in line.lower() for line in stderr_lines)
    success = exec_result["exit_code"] == 0 and not has_traceback and not has_exception
    return {
        **exec_result,
        "success": success,
        "error_summary": None if success else (stderr_lines[-1] if stderr_lines else "Process exited unsuccessfully"),
    }


@traceable(name="execute_and_diagnose")
def execute_and_diagnose(command: TerminalCommand, cwd: Path, timeout: int = 300, retry_count: int = 0) -> dict:
    run = get_current_run_tree()
    if run:
        run.metadata["retry_count"] = retry_count
        run.metadata["command"] = " ".join(command.command)
    try:
        return diagnose_error(run_docker(command, cwd, timeout))
    except subprocess.TimeoutExpired as exc:
        return {"success": False, "stdout": exc.stdout or "", "stderr": exc.stderr or "", "exit_code": -1,
                "error_summary": f"Execution timed out after {timeout} seconds."}
    except Exception as exc:
        return {"success": False, "stdout": "", "stderr": str(exc), "exit_code": -1,
                "error_summary": f"Executor crashed: {exc}"}


def route_to_critic(state: State) -> str:
    if state.executor is None:
        raise ValueError("[EXECUTOR] Executor is None")
    return "DONE" if state.executor.success else "CRITIC"
