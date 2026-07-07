from typing import List
import sys

from accounts import service
from accounts.models import Account


def _prompt(prompt: str) -> str:
    """Prompt the user and return the raw input string."""
    try:
        return input(prompt)
    except EOFError:
        # Treat EOF as exit command
        print("\nReceived EOF, exiting.")
        sys.exit(0)


def _print_accounts(accounts: List[Account]) -> None:
    """Print a numbered list of accounts."""
    if not accounts:
        print("No accounts found.")
        return
    print("Accounts:")
    for i, acc in enumerate(accounts, start=1):
        print(f" {i}. {acc.owner} | {acc.currency} {acc.balance:.2f} | created: {acc.created_at}")


def _create_account() -> None:
    """Collect input and create a new account."""
    name = _prompt("Owner name: ").strip()
    if not name:
        print("Owner name cannot be empty.")
        return
    bal_str = _prompt("Initial balance (e.g. 100.00): ").strip()
    try:
        balance = float(bal_str)
    except ValueError:
        print("Invalid balance. Must be a number.")
        return
    currency = _prompt("Currency (e.g. USD): ").strip() or "USD"
    try:
        acc = service.create_account(name=name, balance=balance, currency=currency)
        print(f"Created account for {acc.owner} with id {acc.id}.")
    except ValueError as e:
        print(f"Error: {e}")


def _update_account() -> None:
    """Update an existing account's details by index."""
    accounts = service.list_accounts()
    if not accounts:
        print("No accounts to update.")
        return
    _print_accounts(accounts)
    idx_str = _prompt("Select account number to update: ").strip()
    try:
        idx = int(idx_str)
        if idx < 1 or idx > len(accounts):
            raise IndexError
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    new_name = _prompt("New owner name (leave blank to keep): ").strip()
    new_balance_str = _prompt("New balance (leave blank to keep): ").strip()
    new_currency = _prompt("New currency (leave blank to keep): ").strip()
    try:
        new_balance = None
        if new_balance_str:
            new_balance = float(new_balance_str)
        updated = service.update_account(index=idx - 1, owner=new_name or None, balance=new_balance, currency=new_currency or None)
        print(f"Updated account: {updated.owner} | {updated.currency} {updated.balance:.2f}")
    except ValueError as e:
        print(f"Error: {e}")


def _view_account() -> None:
    """Show details for a selected account by index."""
    accounts = service.list_accounts()
    if not accounts:
        print("No accounts available.")
        return
    _print_accounts(accounts)
    idx_str = _prompt("Select account number to view: ").strip()
    try:
        idx = int(idx_str)
        acc = service.get_account_by_index(idx - 1)
        print(f"Account details:\n ID: {acc.id}\n Owner: {acc.owner}\n Balance: {acc.currency} {acc.balance:.2f}\n Created: {acc.created_at}")
    except (ValueError, IndexError) as e:
        print(f"Error: {e}")


def _transfer() -> None:
    """Transfer funds between two accounts selected by index."""
    accounts = service.list_accounts()
    if len(accounts) < 2:
        print("At least two accounts are required for a transfer.")
        return
    _print_accounts(accounts)
    try:
        src_str = _prompt("Source account number: ").strip()
        dst_str = _prompt("Target account number: ").strip()
        amt_str = _prompt("Amount to transfer: ").strip()
        src = int(src_str) - 1
        dst = int(dst_str) - 1
        amount = float(amt_str)
        service.transfer_funds(src_index=src, dst_index=dst, amount=amount)
        print("Transfer completed.")
    except ValueError:
        print("Invalid numeric input.")
    except IndexError:
        print("Account selection out of range.")
    except Exception as e:
        print(f"Error: {e}")


def _delete_account() -> None:
    """Delete an account after confirmation by index."""
    accounts = service.list_accounts()
    if not accounts:
        print("No accounts to delete.")
        return
    _print_accounts(accounts)
    idx_str = _prompt("Select account number to delete: ").strip()
    try:
        idx = int(idx_str)
        if idx < 1 or idx > len(accounts):
            raise IndexError
    except (ValueError, IndexError):
        print("Invalid selection.")
        return
    confirm = _prompt(f"Type 'y' to confirm deletion of account {idx}: ").strip().lower()
    if confirm != "y":
        print("Deletion cancelled.")
        return
    try:
        service.delete_account(index=idx - 1)
        print("Account deleted.")
    except Exception as e:
        print(f"Error: {e}")


def run_cli() -> None:
    """Main interactive loop for the accounts manager CLI."""
    MENU = (
        "0) Exit",
        "1) Create account",
        "2) Update account",
        "3) View account",
        "4) Transfer funds",
        "5) Delete account",
        "6) List accounts",
    )
    while True:
        print("\nAccounts Manager - choose an option:")
        for line in MENU:
            print(line)
        choice = _prompt("> ").strip()
        if choice == "0":
            print("Exiting.")
            break
        elif choice == "1":
            _create_account()
        elif choice == "2":
            _update_account()
        elif choice == "3":
            _view_account()
        elif choice == "4":
            _transfer()
        elif choice == "5":
            _delete_account()
        elif choice == "6":
            _print_accounts(service.list_accounts())
        else:
            print("Unknown option. Enter 0-6.")
