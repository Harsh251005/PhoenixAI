from src.config.settings import settings
from src.model.schema import State, CriticDecision
from src.prompts.critic_prompt import CRITIC_PROMPT, build_critic_prompt

from langsmith import traceable
from langchain.messages import SystemMessage, HumanMessage

structured_llm = settings.llm.with_structured_output(CriticDecision)


@traceable(run_type="llm", name="critic_agent")
def critic_node(state: State):
    """Evaluate execution output; on failure, flag the specific files the coder should fix."""

    print("CRITIC AGENT IN PROGRESS...")

    user_prompt = build_critic_prompt(state)

    try:
        messages = [
            SystemMessage(content=CRITIC_PROMPT),
            HumanMessage(content=user_prompt),
        ]
        result = structured_llm.invoke(messages)

        return {
            "critic": result
        }

    except Exception as e:
        raise RuntimeError(f"Critic LLM call failed: {e}") from e


def route_from_critic_to_coder(state: State) -> str:

    if state.critic is None:
        raise ValueError("[CRITIC] Critic is None")

    if state.critic.status == "pass":
        return "DONE"

    elif state.retry_fix >= 3:
        return "GIVE_UP"

    else:
        return "RETRY"
