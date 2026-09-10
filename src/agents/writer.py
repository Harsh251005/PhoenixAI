from langsmith import traceable

from src.config.settings import settings
from src.model.schema import State


@traceable(run_type="tool", name="writer_agent")
def writer_node(state: State) -> State:
    """Write generated files while enforcing project and file path boundaries."""
    print("WRITER AGENT IN PROGRESS...")
    if state.project is None:
        raise ValueError("[WRITER] Project is None")

    project_name = state.project.project_name.strip()
    if not project_name or project_name in {".", ".."} or "/" in project_name or "\\" in project_name:
        raise ValueError(f"[WRITER] Unsafe project name: {project_name!r}")

    root = settings.GENERATED_PROJECTS_DIR.resolve()
    root.mkdir(parents=True, exist_ok=True)
    project_dir = (root / project_name).resolve()
    if not project_dir.is_relative_to(root):
        raise ValueError(f"[WRITER] Unsafe project name: {project_name!r}")
    project_dir.mkdir(parents=True, exist_ok=True)

    for generated_file in state.project.files:
        file_path = (project_dir / generated_file.file_path).resolve()
        if not file_path.is_relative_to(project_dir):
            raise ValueError(f"Unsafe file path from coder: {generated_file.file_path!r}")
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(generated_file.file_content, encoding="utf-8")

    # Keep the model's directory metadata consistent with the actual trusted path.
    state.project.project_directory = str(project_dir)
    return state
