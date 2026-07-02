from src.config.settings import settings
from src.model.schema import State, ProjectOutput
from src.prompts.coder_prompt import CODER_PROMPT, build_coder_prompt

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from pathlib import Path
from pydantic import BaseModel

AGENTS_DIR = Path(__file__).resolve().parent
DOCS_DIR = AGENTS_DIR / "documentation"
CODER_DOC = DOCS_DIR / "coder_documentation.jsonl"

llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, api_key=settings.OPENAI_API_KEY)

structured_llm = llm.with_structured_output(ProjectOutput)


def write_documentation(schema: BaseModel, file_path: Path = Path("coder_documentation.jsonl")) -> None:
    """Append a Pydantic schema instance as a single JSON line to a JSONL file."""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("a", encoding="utf-8") as f:
            f.write(schema.model_dump_json() + "\n")
    except Exception as e:
        raise RuntimeError(f"Failed to write documentation to {file_path}: {e}") from e


def coder_node(state: State) -> dict:

    print("CODER AGENT IN PROGRESS...")

    if state.executor is not None:
        print(f"ATTEMPT: {state.executor.retry_count}")

    user_prompt = build_coder_prompt(state)

    result = structured_llm.invoke(
        [
            SystemMessage(content=CODER_PROMPT),
            HumanMessage(content=user_prompt)
        ]
    )

    write_documentation(
        result.coder_documentation,
        file_path=CODER_DOC
    )

    return {
        "project": result
    }
