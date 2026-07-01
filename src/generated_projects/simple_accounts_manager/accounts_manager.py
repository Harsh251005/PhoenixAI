from typing import Dict, List, Union

class Account:
    """Represents a bank account with a user and balance."""
    def __init__(self, user: str, balance: float = 0.0) -> None:
        self.user = user
        self.balance = balance

    def deposit(self, amount: float) -> None:
        """Deposit an amount to the account."""
        if amount < 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        """Withdraw an amount from the account."""
        if amount < 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds for this withdrawal.")
        self.balance -= amount

    def get_balance(self) -> float:
        """Get the current balance of the account."""
        return self.balance

class AccountManager:
    """Manages multiple accounts."""
    def __init__(self) -> None:
        self.accounts: Dict[str, Account] = {}

    def create_account(self, user: str) -> None:
        """Create a new account for a user."""
        if user in self.accounts:
            raise ValueError(f"Account for user '{user}' already exists.")
        self.accounts[user] = Account(user)

    def deposit_to_account(self, user: str, amount: float) -> None:
        """Deposit an amount to a user's account."""
        if user not in self.accounts:
            raise ValueError(f"Account for user '{user}' does not exist.")
        self.accounts[user].deposit(amount)

    def withdraw_from_account(self, user: str, amount: float) -> None:
        """Withdraw an amount from a user's account."""
        if user not in self.accounts:
            raise ValueError(f"Account for user '{user}' does not exist.")
        self.accounts[user].withdraw(amount)

    def get_account_balance(self, user: str) -> float:
        """Get the balance for a user's account."""
        if user not in self.accounts:
            raise ValueError(f"Account for user '{user}' does not exist.")
        return self.accounts[user].get_balance()

def main() -> None:
    """Main function to demonstrate the account management system."""
    manager = AccountManager()
    try:
        manager.create_account("Alice")
        manager.deposit_to_account("Alice", 100.0)
        manager.withdraw_from_account("Alice", 50.0)
        balance = manager.get_account_balance("Alice")
        print(f"Alice's balance: ${balance:.2f}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
