import random


def get_random_number(min_val: int, max_val: int) -> int:
    """Generate a random number between min_val and max_val."""
    return random.randint(min_val, max_val)


def evaluate_guess(guess: int, secret_number: int) -> str:
    """Evaluate the user's guess against the secret number."""
    if guess < secret_number:
        return "Too low!"
    elif guess > secret_number:
        return "Too high!"
    else:
        return "Correct!"


def play_game(min_val: int, max_val: int, guesses: list) -> None:
    """Main logic for playing the guessing game."""
    secret_number = get_random_number(min_val, max_val)
    print(f"Guess the number between {min_val} and {max_val}!")
    attempts = 0

    for guess in guesses:
        attempts += 1
        result = evaluate_guess(guess, secret_number)
        print(f"Your guess: {guess} - {result}")
        if result == "Correct!":
            print(f"You guessed it in {attempts} attempts!")
            break
    else:
        print(f"You didn't guess the number. It was: {secret_number}")


def main() -> None:
    """Entry point for the game."""
    min_val = 1
    max_val = 100
    print("Welcome to the Number Guessing Game!")
    # Hardcoded guesses for demonstration, replace with user-supplied values in real use.
    guesses = [45, 30, 55, 100, 87]
    play_game(min_val, max_val, guesses)


if __name__ == "__main__":
    main()