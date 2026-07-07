from src.graph import graph_builder
from src.model.schema import State
import json

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
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


def run_task(graph, task: str) -> State:
    """Invoke the graph for a single task and return the final state."""
    console.print(f'\n[bold green]🚀 Generating:[/bold green] "{task}"...\n')

    try:
        final_state = graph.invoke(State(user_input=task))
        console.print("\n[bold green]✅ Done![/bold green] Check the generated project folder.\n")
        return final_state

    except Exception as e:
        console.print(f"\n[bold red]❌ Something went wrong:[/bold red] {e}\n")
        raise


def print_final_state(final_state) -> None:
    """Pretty-print the full final state as syntax-highlighted JSON."""
    data = final_state.model_dump(mode="json") if hasattr(final_state, "model_dump") else dict(final_state)
    json_str = json.dumps(data, indent=4, default=str)

    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False, word_wrap=True)
    console.print(
        Panel(
            syntax,
            title="[bold white]FINAL AGENT STATE[/bold white]",
            border_style="cyan",
            expand=True,
        )
    )


def main() -> None:
    """Run the Phoenix AI agent."""
    console.print(Text(BANNER, style="bold magenta"))

    graph = graph_builder()

    task = get_user_input()
    final_state = run_task(graph, task)

    console.print()
    print_final_state(final_state)


if __name__ == "__main__":
    main()