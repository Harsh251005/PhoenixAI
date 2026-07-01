from src.config.settings import settings
from src.model.schema import State



def writer_node(state: State) -> State:

    print("WRITER AGENT IN PROGRESS...")

    settings.GENERATED_PROJECTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if state.project.project_name is None:
        raise ValueError(
            "No project generated."
        )

    project_dir = (
        settings.GENERATED_PROJECTS_DIR
        / state.project.project_name
    )

    project_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    file = state.project.file

    file_path = (
        project_dir
        / file.file_name
    )

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path.write_text(
        file.file_content,
        encoding="utf-8"
    )

    return state