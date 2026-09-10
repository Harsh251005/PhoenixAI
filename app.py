from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.graph import graph_builder
from src.model.schema import State

app = FastAPI(title="Phoenix AI")


class BuildRequest(BaseModel):
    """Request body for a project-generation job."""

    prompt: str = Field(min_length=1, description="Plain-English project request")


@app.get("/")
def root() -> dict[str, str]:
    """Return a lightweight service status response."""
    return {"message": "Phoenix AI", "status": "ok"}


def _result_summary(state: State | dict) -> dict:
    """Return useful job metadata without exposing the complete internal state."""
    def get(name: str, default=None):
        return state.get(name, default) if isinstance(state, dict) else getattr(state, name, default)

    project = get("project")
    executor = get("executor")

    def nested(value, name: str, default=None):
        return value.get(name, default) if isinstance(value, dict) else getattr(value, name, default)

    return {
        "project_name": nested(project, "project_name"),
        "project_directory": nested(project, "project_directory"),
        "description": nested(project, "description"),
        "success": nested(executor, "success", False),
        "stdout": nested(executor, "stdout", ""),
        "stderr": nested(executor, "stderr", ""),
        "error_summary": nested(executor, "error_summary") or "Generation did not complete.",
        "retry_count": get("retry_fix", 0),
    }


@app.post("/build")
def build(request: BuildRequest) -> dict:
    """Generate a project and return a concise execution summary."""
    graph = graph_builder()
    final_state = graph.invoke(State(user_input=request.prompt.strip()))
    return {"result": _result_summary(final_state)}
