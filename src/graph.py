from src.agents.coder import coder_node
from src.agents.writer import writer_node
from src.agents.executor import executor_node, route_after_execution
from src.model.schema import State

from langgraph.graph import StateGraph, START, END

def graph_builder():
    builder = StateGraph(State)

    builder.add_node("coder", coder_node)
    builder.add_node("writer", writer_node)
    builder.add_node("executor", executor_node)


    builder.add_edge(START, "coder")
    builder.add_edge("coder", "writer")
    builder.add_edge("writer", "executor")

    builder.add_conditional_edges(
        "executor",
        route_after_execution,
        {
            "done": END,
            "give_up": END,
            "retry_coder": "coder",
        }
    )

    graph = builder.compile()

    save_graph(graph)

    return graph



def save_graph(graph) -> None:
    png_data = graph.get_graph().draw_mermaid_png()

    with open("langgraph.png", "wb") as f:
        f.write(png_data)

    print("Graph saved to langgraph.png\n")