from src.config.settings import settings
from src.model.schema import State, ProjectOutput
from src.prompts.coder_prompt import CODER_PROMPT, build_coder_prompt

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, api_key=settings.OPENAI_API_KEY)

structured_llm = llm.with_structured_output(ProjectOutput)

def coder_node(state: State) -> State:

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

    state.project = result

    return state