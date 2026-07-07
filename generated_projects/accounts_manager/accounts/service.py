from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from .models import Account
from .storage import load_accounts, save_accounts


def list_accounts() -> List[Account]:
    """Return the current list of accounts from storage."""
    return load_accounts()


def create_account(name: str, balance: float, currency: str = "USD") -> Account:
    """Create a new account with the specified owner, balance and currency and persist it."""
    if balance < 0:
        raise ValueError("Initial balance cannot be negative.")
    acc = Account(
        id=str(uuid4()),
        owner=name,
        balance=round(float(balance), 2),
        currency=currency.upper(),
        created_at=datetime.utcnow().isoformat(),
    )
    accounts = load_accounts()
    accounts.append(acc)
    save_accounts(accounts)
    return acc


def get_account_by_index(index: int) -> Account:
    """Retrieve an account by zero-based index; raises IndexError if out of range."""
    accounts = load_accounts()
    if index < 0 or index >= len(accounts):
        raise IndexError("Account index out of range.")
    return accounts[index]


def update_account(index: int, owner: Optional[str] = None, balance: Optional[float] = None, currency: Optional[str] = None) -> Account:
    """Update fields of an account by zero-based index and persist changes."""
    accounts = load_accounts()
    if index < 0 or index >= len(accounts):
        raise IndexError("Account index out of range.")
    acc = accounts[index]
    if owner is not None and owner.strip():
        acc.owner = owner.strip()
    if balance is not None:
        if balance < 0:
            raise ValueError("Balance cannot be negative.")
        acc.balance = round(float(balance), 2)
    if currency is not None and currency.strip():
        acc.currency = currency.strip().upper()
    save_accounts(accounts)
    return acc


def delete_account(index: int) -> None:
    """Delete an account by zero-based index and persist the change."""
    accounts = load_accounts()
    if index < 0 or index >= len(accounts):
        raise IndexError("Account index out of range.")
    accounts.pop(index)
    save_accounts(accounts)


def transfer_funds(src_index: int, dst_index: int, amount: float) -> None:
    """Transfer amount from source to destination account by zero-based indices with validation."""
    if amount <= 0:
        raise ValueError("Transfer amount must be positive.")
    accounts = load_accounts()
    if src_index < 0 or src_index >= len(accounts) or dst_index < 0 or dst_index >= len(accounts):
        raise IndexError("Account index out of range.")
    if src_index == dst_index:
        raise ValueError("Source and destination accounts must be different.")
    src = accounts[src_index]
    dst = accounts[dst_index]
    if src.currency != dst.currency:
        raise ValueError("Currency mismatch: only same-currency transfers are supported.")
    if src.balance < amount:
        raise ValueError("Insufficient funds in source account.")
    src.balance = round(src.balance - float(amount), 2)
    dst.balance = round(dst.balance + float(amount), 2)
    save_accounts(accounts)
