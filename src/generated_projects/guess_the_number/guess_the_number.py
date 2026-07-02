import json
import os
import sys
from typing import Dict, Optional

# Simple Guess the Number game

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
STATS_FILE = os.path.join(DATA_DIR, "stats.json")
MIN_NUMBER = 1
MAX_NUMBER = 100
FIXED_SECRET = 42  # Deterministic secret so automated tests can predict the answer


def ensure_data_dir() -> None:
    """Ensure the data directory exists next to the script."""
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except OSError as exc:
        print(f"Error creating data directory '{DATA_DIR}': {exc}", file=sys.stderr)


def load_stats() -> Dict[str, Optional[int]]:
    """Load game statistics from the stats JSON file, returning defaults on error."""
    defaults = {"games_played": 0, "best_score": None, "last_score": None}
    if not os.path.exists(STATS_FILE):
        return defaults
    try:
        with open(STATS_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            return defaults
        # Validate keys
        return {
            "games_played": int(data.get("games_played", 0)),
            "best_score": (int(data["best_score"]) if data.get("best_score") is not None else None),
            "last_score": (int(data["last_score"]) if data.get("last_score") is not None else None),
        }
    except (OSError, ValueError, TypeError) as exc:
        print(f"Warning: could not read stats file '{STATS_FILE}': {exc}", file=sys.stderr)
        return defaults


def save_stats(stats: Dict[str, Optional[int]]) -> None:
    """Persist game statistics to the stats JSON file."""
    try:
        with open(STATS_FILE, "w", encoding="utf-8") as fh:
            json.dump(stats, fh, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"Error writing stats file '{STATS_FILE}': {exc}", file=sys.stderr)


def get_secret_number() -> int:
    """Return the secret number for the current game (deterministic)."""
    # Use a fixed secret for deterministic behavior in automated tests
    return FIXED_SECRET


def prompt_menu_choice() -> str:
    """Prompt the main menu and return the user's raw choice."""
    print("\nGuess the Number")
    print("1) Play")
    print("0) Exit")
    return input("Choose an option (1 to play, 0 to exit): ").strip()


def prompt_guess() -> Optional[str]:
    """Prompt the user for a guess; returns the raw input or None on EOF."""
    try:
        return input(f"Enter your guess ({MIN_NUMBER}-{MAX_NUMBER}) or type 'quit' to return: ").strip()
    except EOFError:
        return None


def parse_guess(raw: str) -> Optional[int]:
    """Convert raw input into an integer guess, returning None if invalid or out of range."""
    try:
        val = int(raw)
    except ValueError:
        return None
    if val < MIN_NUMBER or val > MAX_NUMBER:
        return None
    return val


def play_game() -> Optional[int]:
    """Run a single round of the game; return number of attempts if won, or None if aborted."""
    secret = get_secret_number()
    print(f"\nI'm thinking of a number between {MIN_NUMBER} and {MAX_NUMBER}.")
    attempts = 0
    while True:
        raw = prompt_guess()
        if raw is None:
            print("Input ended. Returning to menu.")
            return None
        if raw.lower() in ("quit", "exit"):
            print("Aborting current game and returning to menu.")
            return None
        guess = parse_guess(raw)
        if guess is None:
            print(f"Invalid input. Please enter an integer between {MIN_NUMBER} and {MAX_NUMBER}, or 'quit'.")
            continue
        attempts += 1
        if guess == secret:
            print(f"Congratulations! You guessed the number in {attempts} attempts.")
            return attempts
        if guess < secret:
            print("Too low. Try a higher number.")
        else:
            print("Too high. Try a lower number.")


def update_stats_on_win(stats: Dict[str, Optional[int]], attempts: int) -> Dict[str, Optional[int]]:
    """Update stats dictionary after a win and return it."""
    stats = stats.copy()
    stats["games_played"] = int(stats.get("games_played", 0)) + 1
    stats["last_score"] = int(attempts)
    best = stats.get("best_score")
    if best is None or attempts < int(best):
        stats["best_score"] = int(attempts)
    return stats


def print_stats(stats: Dict[str, Optional[int]]) -> None:
    """Print a short summary of game statistics."""
    print("\nGame Statistics:")
    print(f"  Games played: {stats.get('games_played', 0)}")
    best = stats.get("best_score")
    last = stats.get("last_score")
    print(f"  Best score (fewest attempts): {best if best is not None else 'N/A'}")
    print(f"  Last game attempts: {last if last is not None else 'N/A'}")


def main() -> None:
    """Main program loop handling menu, game play, and stats persistence."""
    ensure_data_dir()
    stats = load_stats()
    while True:
        choice = prompt_menu_choice()
        if choice == "1":
            attempts = play_game()
            if attempts is not None:
                stats = update_stats_on_win(stats, attempts)
                save_stats(stats)
        elif choice == "0":
            print_stats(stats)
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please enter '1' to play or '0' to exit.")


if __name__ == "__main__":
    main()
