from src.config.settings import settings
from src.model.schema import State, GeneratedFile
from src.prompts.coder_prompt import CODER_PROMPT

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatOpenAI(model=settings.OPENAI_MODEL_NAME, api_key=settings.OPENAI_API_KEY)

structured_llm = llm.with_structured_output(GeneratedFile)

def coder_node(state: State) -> State:
    """
    Generates a single Python file.
    """

    print("CODER AGENT IN PROGRESS...")

    result = structured_llm.invoke(
        [
            SystemMessage(content=CODER_PROMPT),
            HumanMessage(content=state.user_input)
        ]
    )

    state.generated_file = result

    return state