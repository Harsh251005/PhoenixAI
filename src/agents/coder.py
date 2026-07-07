from src.config.settings import settings
from src.model.schema import State, ProjectOutput, FixOutput
from src.prompts.coder_prompt import CODER_PROMPT, build_coder_prompt

from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable


@traceable(run_type="llm", name="coder_agent")
def coder_node(state: State):
    """Generate a full project on first run, or patch specific flagged files on retry."""

    print("CODER AGENT IN PROGRESS...")

    is_fix_mode = state.project is not None and state.project.project_name is not None

    user_prompt = build_coder_prompt(state)

    if not is_fix_mode:
        # --- FIRST GENERATION: full project schema ---
        structured_llm = settings.llm.with_structured_output(ProjectOutput)

        try:
            messages = [
                SystemMessage(content=CODER_PROMPT),
                HumanMessage(content=user_prompt),
            ]

            output = structured_llm.invoke(messages)

            return {
                "project": output
            }

        except Exception as e:
            raise RuntimeError(f"Coder LLM call failed (initial generation): {e}") from e

    # --- FIX MODE: slim schema, only flagged files come back ---
    structured_llm = settings.llm.with_structured_output(FixOutput)

    try:
        messages = [
            SystemMessage(content=CODER_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        output = structured_llm.invoke(messages)

    except Exception as e:
        raise RuntimeError(f"Coder LLM call failed (fix mode): {e}") from e

    if state.project is None:
        raise ValueError("[CODER] Project is None")

    # Only update fixed files
    existing_by_path = {f.file_path: f for f in state.project.files}

    for fixed_file in output.fixed_files:
        if fixed_file.file_path not in existing_by_path:
            print(f"[WARN] Coder returned a new/unknown file path: {fixed_file.file_path!r}")
        existing_by_path[fixed_file.file_path] = fixed_file  # update or add

    state.project.files = list(existing_by_path.values())

    if state.executor is not None:
        state.retry_fix += 1

    return state
