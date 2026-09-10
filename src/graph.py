from functools import lru_cache
from pathlib import Path

from langgraph.graph import END, START, StateGraph

from src.agents.coder import coder_node
from src.agents.critic import critic_node, route_from_critic_to_coder
from src.agents.executor import executor_node, route_to_critic
from src.agents.writer import writer_node
from src.config.settings import settings
from src.model.schema import State


@lru_cache(maxsize=1)
def graph_builder():
    """Build and cache the Phoenix generation graph."""
    builder = StateGraph(State)
    builder.add_node("coder", coder_node)
    builder.add_node("writer", writer_node)
    builder.add_node("executor", executor_node)
    builder.add_node("critic", critic_node)
    builder.add_edge(START, "coder")
    builder.add_edge("coder", "writer")
    builder.add_edge("writer", "executor")
    builder.add_conditional_edges("executor", route_to_critic, {"DONE": END, "CRITIC": "critic"})
    builder.add_conditional_edges(
        "critic", route_from_critic_to_coder,
        {"DONE": END, "GIVE_UP": END, "RETRY": "coder"},
    )
    graph = builder.compile()
    save_graph(graph)
    return graph


def save_graph(graph) -> None:
    """Save the graph visualization inside the Phoenix project directory."""
    png_data = graph.get_graph().draw_mermaid_png()
    output_path = Path(settings.PROJECT_ROOT) / "langgraph.png"
    output_path.write_bytes(png_data)
    print(f"Graph saved to {output_path}")
