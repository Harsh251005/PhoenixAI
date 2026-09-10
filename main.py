from src.graph import graph_builder
from src.model.schema import State

from rich.console import Console
from rich.text import Text

console = Console()

BANNER = """
╔══════════════════════════════════════╗
║               Phoenix AI             ║
║       AI Code Generator Agent        ║
╚══════════════════════════════════════╝
"""


def get_user_input() -> str:
    """Prompt the user for a task description, re-asking if left blank."""
    while True:
        task = console.input("\n[bold cyan]📝 What should I build?[/bold cyan] (or 'exit' to quit): ").strip()

        if task.lower() == "exit":
            console.print("\n👋 [yellow]Exiting Phoenix AI.[/yellow]")
            raise SystemExit(0)

        if task:
            return task

        console.print("[red]⚠️  Please enter a task description.[/red]")


def _get(state, name: str, default=None):
    """Read an attribute from state whether it's a State instance or a plain dict."""
    return state.get(name, default) if isinstance(state, dict) else getattr(state, name, default)


def run_task(graph, task: str) -> State:
    """Invoke the graph for a single task, report the outcome, and return the final state."""
    console.print(f'\n[bold green]🚀 Generating:[/bold green] "{task}"...\n')

    try:
        final_state = graph.invoke(State(user_input=task))
    except Exception as e:
        console.print(f"\n[bold red]❌ Something went wrong:[/bold red] {e}\n")
        raise

    executor = _get(final_state, "executor")
    success = _get(executor, "success", False) if executor is not None else False

    if success:
        console.print("\n[bold green]✅ Done![/bold green] Check the generated project folder.\n")
    else:
        critic = _get(final_state, "critic")
        reasoning = _get(critic, "reasoning", None) if critic is not None else None
        retry_fix = _get(final_state, "retry_fix", 0)
        console.print(
            f"\n[bold red]❌ Gave up after {retry_fix} retry attempt(s).[/bold red] "
            "The generated project still fails to execute."
        )
        if reasoning:
            console.print(f"[yellow]Last critic reasoning:[/yellow] {reasoning}\n")

    return final_state


def main() -> None:
    """Run the Phoenix AI agent."""
    console.print(Text(BANNER, style="bold magenta"))

    graph = graph_builder()

    task = get_user_input()
    run_task(graph, task)

    console.print()


if __name__ == "__main__":
    main()