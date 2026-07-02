import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

# ----------------------
# Configuration / Paths
# ----------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TASKS_FILE = DATA_DIR / "tasks.json"

# ----------------------
# Helpers
# ----------------------

def ensure_data_dir() -> None:
    """Ensure the data directory exists on disk."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"Error creating data directory '{DATA_DIR}': {e}")
        sys.exit(1)


def read_json_file(path: Path, default):
    """Read a JSON file returning default on errors or non-matching types."""
    ensure_data_dir()
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError:
        # Backup the corrupt file then return default
        try:
            backup = path.with_suffix(path.suffix + ".corrupt")
            path.rename(backup)
            print(f"Warning: corrupt file renamed to {backup}. Starting fresh.")
        except OSError as e:
            print(f"Warning: failed to backup corrupt file: {e}")
        return default
    except OSError as e:
        print(f"Error reading file '{path}': {e}")
        return default


def write_json_file(path: Path, data) -> bool:
    """Write JSON data to a file; returns True on success, False on failure."""
    ensure_data_dir()
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError as e:
        print(f"Error writing to '{path}': {e}")
        return False


def now_isoutc() -> str:
    """Return current UTC time as ISO8601 string (timezone-aware)."""
    return datetime.now(timezone.utc).isoformat()


def next_task_id(tasks: List[Dict]) -> int:
    """Compute the next numerical task id based on existing tasks."""
    if not tasks:
        return 1
    try:
        max_id = max(int(t.get("id", 0)) for t in tasks)
        return max_id + 1
    except Exception:
        return 1


def format_task(task: Dict) -> str:
    """Format a single task into an ASCII-safe one-line string."""
    status = "x" if task.get("completed") else " "
    created = task.get("created_at", "?")
    desc = task.get("description", "")
    tid = task.get("id", "?")
    return f"[{status}] {tid}: {desc} (created: {created})"


# ----------------------
# Core operations
# ----------------------

def load_tasks() -> List[Dict]:
    """Load the list of tasks from persistent storage."""
    data = read_json_file(TASKS_FILE, [])
    if not isinstance(data, list):
        print("Warning: tasks file malformed (not a list). Reinitializing.")
        return []
    return data


def save_tasks(tasks: List[Dict]) -> None:
    """Persist the list of tasks to disk."""
    success = write_json_file(TASKS_FILE, tasks)
    if not success:
        print("Warning: failed to save tasks.")


def add_task(description: str) -> None:
    """Add a new task with the supplied description."""
    if not description.strip():
        print("Cannot add an empty task.")
        return
    tasks = load_tasks()
    tid = next_task_id(tasks)
    task = {
        "id": tid,
        "description": description.strip(),
        "created_at": now_isoutc(),
        "completed": False,
        "completed_at": None,
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"Task added with id {tid}.")


def list_tasks() -> None:
    """Print all stored tasks in a human-readable form."""
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    print("Tasks:")
    for task in sorted(tasks, key=lambda x: int(x.get("id", 0))):
        try:
            print("  " + format_task(task))
        except UnicodeEncodeError:
            # Fallback: ensure ASCII-only output
            safe = format_task(task).encode("ascii", errors="replace").decode("ascii")
            print("  " + safe)


def mark_completed(task_id: int) -> None:
    """Mark the task with the given id as completed."""
    tasks = load_tasks()
    for task in tasks:
        try:
            if int(task.get("id", -1)) == task_id:
                if task.get("completed"):
                    print(f"Task {task_id} is already completed.")
                    return
                task["completed"] = True
                task["completed_at"] = now_isoutc()
                save_tasks(tasks)
                print(f"Task {task_id} marked completed.")
                return
        except (ValueError, TypeError):
            continue
    print(f"Task with id {task_id} not found.")


def delete_task(task_id: int) -> None:
    """Delete the task with the specified id."""
    tasks = load_tasks()
    new_tasks = [t for t in tasks if int(t.get("id", -1)) != task_id]
    if len(new_tasks) == len(tasks):
        print(f"Task with id {task_id} not found.")
        return
    save_tasks(new_tasks)
    print(f"Task {task_id} deleted.")


# ----------------------
# User interface
# ----------------------

def print_menu() -> None:
    """Display the main menu choices to the user."""
    print("\nSimple To-Do List Manager")
    print("1) Add task")
    print("2) List tasks")
    print("3) Mark task completed")
    print("4) Delete task")
    print("0) Exit")


def prompt_input(prompt: str) -> str:
    """Prompt the user for input and return the stripped response; treat EOF/interrupt as '0'."""
    try:
        return input(prompt).strip()
    except EOFError:
        return "0"
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")
        return "0"


# ----------------------
# Main program
# ----------------------

def main_loop() -> None:
    """Run the interactive program loop until the user exits."""
    print("Welcome! This program stores tasks in 'data/tasks.json'. Type 0 to exit.")
    while True:
        print_menu()
        choice = prompt_input("Select an option: ")
        if choice == "0":
            print("Goodbye!")
            break
        if choice == "1":
            desc = prompt_input("Enter task description (or 0 to cancel): ")
            if desc == "0" or desc == "":
                print("Add cancelled.")
                continue
            add_task(desc)
            continue
        if choice == "2":
            list_tasks()
            continue
        if choice == "3":
            id_str = prompt_input("Enter task id to mark completed (or 0 to cancel): ")
            if id_str == "0":
                print("Operation cancelled.")
                continue
            try:
                tid = int(id_str)
                mark_completed(tid)
            except ValueError:
                print("Invalid id. Please enter a number.")
            continue
        if choice == "4":
            id_str = prompt_input("Enter task id to delete (or 0 to cancel): ")
            if id_str == "0":
                print("Delete cancelled.")
                continue
            try:
                tid = int(id_str)
                delete_task(tid)
            except ValueError:
                print("Invalid id. Please enter a number.")
            continue
        print("Unknown option. Please choose a valid number.")


if __name__ == "__main__":
    try:
        main_loop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
