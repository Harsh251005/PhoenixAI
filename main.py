from src.graph import graph_builder
from src.model.schema import State

def main():
    graph = graph_builder()

    user_input = "Create 2 simple agents using langgraph"

    result = graph.invoke(
        State(
            user_input=user_input
        )
    )

if __name__ == "__main__":
    main()