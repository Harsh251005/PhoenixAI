from pathlib import Path

from src.model.schema import State

PROJECT_ROOT = Path(__file__).resolve().parent.parent

GENERATED_PROJECTS_DIR = PROJECT_ROOT / Path("generated_projects")

def writer_node(state: State) -> State:

    print("WRITER AGENT IN PROGRESS...")

    GENERATED_PROJECTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if state.generated_file is None:
        raise ValueError(
            "No generated file found in state."
        )

    project_dir = (
        GENERATED_PROJECTS_DIR
        / state.generated_file.project_name
    )

    project_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = (
        project_dir
        / state.generated_file.file_name
    )

    file_path.write_text(
        state.generated_file.file_content,
        encoding="utf-8"
    )

    return state