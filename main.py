from src.graph import graph_builder
from src.model.schema import State


BANNER = """
╔══════════════════════════════════════╗
║               Phoenix AI             ║
║       AI Code Generator Agent        ║
╚══════════════════════════════════════╝
"""


def get_user_input() -> str:
    """Prompt the user for a task description, re-asking if left blank."""
    while True:
        task = input("\n📝 What should I build? (or 'exit' to quit): ").strip()
        if task:
            return task
        print("⚠️  Please enter a task description.")


def run_task(graph, task: str) -> None:
    """Invoke the graph for a single task and report success or failure."""
    print(f"\n🚀 Generating: \"{task}\"...\n")
    try:
        graph.invoke(State(user_input=task))
        print("\n✅ Done! Check the generated project folder.\n")
    except Exception as e:
        print(f"\n❌ Something went wrong: {e}\n")


def main() -> None:
    """Run an interactive loop that generates code projects from user input."""
    print(BANNER)
    graph = graph_builder()

    while True:
        task = get_user_input()
        if task.lower() in {"exit", "quit", "q"}:
            print("\n👋 Goodbye!\n")
            break
        run_task(graph, task)


if __name__ == "__main__":
    main()