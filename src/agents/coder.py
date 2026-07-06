import json

from src.config.settings import settings
from src.model.schema import State, ProjectOutput
from src.prompts.coder_prompt import CODER_PROMPT, build_coder_prompt

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langsmith import traceable

llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, api_key=settings.OPENAI_API_KEY)

structured_llm = llm.with_structured_output(ProjectOutput)


@traceable(run_type="llm", name="coder_agent")
def coder_node(state: State) -> dict:

    print("CODER AGENT IN PROGRESS...")

    user_prompt = build_coder_prompt(state)

    result = structured_llm.invoke(
        [
            SystemMessage(content=CODER_PROMPT),
            HumanMessage(content=user_prompt)
        ]
    )

    return {
        "project": result
    }
