import json
import os
from typing import List, Dict, Any


class JSONStorage:
    """Simple JSON list storage stored in a file under a provided base directory's data/ folder."""

    def __init__(self, filename: str, base_dir: str) -> None:
        """Create storage for filename; ensures data directory exists and file initializes to an empty list if missing or invalid."""
        self.base_dir = base_dir
        self.data_dir = os.path.join(self.base_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.path = os.path.join(self.data_dir, filename)
        # Initialize file if missing or invalid
        try:
            if not os.path.exists(self.path):
                self._write_list([])
            else:
                # Validate JSON; if corrupt, reinitialize
                self._read_list()
        except Exception:
            # On any read error, reinitialize the storage file to an empty list
            try:
                self._write_list([])
            except Exception as exc:
                raise RuntimeError(f"Failed to initialize storage file {self.path}: {exc}")

    def _read_list(self) -> List[Dict[str, Any]]:
        """Read the JSON file and return a list of dictionaries; handles decode errors gracefully."""
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if not isinstance(data, list):
                    raise ValueError("Storage file does not contain a list")
                return data
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            raise RuntimeError(f"Corrupt JSON in storage file: {self.path}")

    def _write_list(self, data: List[Dict[str, Any]]) -> None:
        """Write the provided list of dictionaries to the storage file with UTF-8 encoding."""
        try:
            with open(self.path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except Exception as exc:
            raise RuntimeError(f"Failed to write storage file {self.path}: {exc}")

    def read_all(self) -> List[Dict[str, Any]]:
        """Public: read and return all stored records as a list of dictionaries."""
        return self._read_list()

    def save_all(self, items: List[Dict[str, Any]]) -> None:
        """Public: overwrite storage with the provided list of dictionaries."""
        self._write_list(items)
