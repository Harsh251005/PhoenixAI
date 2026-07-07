from pathlib import Path
import json
from typing import List
from json import JSONDecodeError

from .models import Account


DATA_DIR_NAME = "data"
ACCOUNTS_FILE_NAME = "accounts.json"


def _get_data_file_path() -> Path:
    """Return the Path to the accounts JSON file under the project root data/ directory."""
    root = Path(__file__).resolve().parents[1]
    data_dir = root / DATA_DIR_NAME
    data_dir.mkdir(exist_ok=True)
    return data_dir / ACCOUNTS_FILE_NAME


def load_accounts() -> List[Account]:
    """Load accounts from the JSON file, returning an empty list on missing or corrupt files."""
    path = _get_data_file_path()
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
            if not isinstance(raw, list):
                # Corrupt or unexpected format; reinitialize
                return []
            return [Account.from_dict(item) for item in raw]
    except JSONDecodeError:
        # Corrupt JSON: overwrite on next save by returning empty
        return []
    except Exception as e:
        raise IOError(f"Failed to read accounts file: {e}")


def save_accounts(accounts: List[Account]) -> None:
    """Save the provided list of accounts to the JSON file safely."""
    path = _get_data_file_path()
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump([a.to_dict() for a in accounts], f, ensure_ascii=False, indent=2)
    except Exception as e:
        raise IOError(f"Failed to write accounts file: {e}")
