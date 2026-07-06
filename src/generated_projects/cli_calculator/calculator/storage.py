from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
HISTORY_FILE = DATA_DIR / "history.json"


def _ensure_data_dir() -> None:
    """Create the data directory if it does not exist."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise OSError(f"Failed to create data directory '{DATA_DIR}': {exc}")


def load_history() -> List[Dict[str, Any]]:
    """Load history from the JSON file, returning a list of history entries.

    Initializes an empty list if the file is missing or corrupt.
    """
    _ensure_data_dir()
    if not HISTORY_FILE.exists():
        return []
    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, list):
                return data
            # If the file contains something else, reinitialize
            return []
    except json.JSONDecodeError:
        # Corrupt file: overwrite with empty list and return []
        try:
            save_history([])
        except Exception as exc:
            raise RuntimeError(f"History file corrupt and failed to reinitialize: {exc}")
        return []
    except OSError as exc:
        raise OSError(f"Failed to read history file '{HISTORY_FILE}': {exc}")


def save_history(history: List[Dict[str, Any]]) -> None:
    """Save the provided history list to the JSON file atomically where possible."""
    _ensure_data_dir()
    try:
        temp = HISTORY_FILE.with_suffix(".tmp")
        with temp.open("w", encoding="utf-8") as fh:
            json.dump(history, fh, indent=2, ensure_ascii=False)
        temp.replace(HISTORY_FILE)
    except OSError as exc:
        raise OSError(f"Failed to write history file '{HISTORY_FILE}': {exc}")


def append_history(entry: Dict[str, Any]) -> None:
    """Append a single entry to history and persist to disk."""
    history = load_history()
    history.append(entry)
    save_history(history)
