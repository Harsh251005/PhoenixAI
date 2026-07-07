from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class Account:
    """Represents a simple account with id, owner, balance, currency and creation time."""
    id: str
    owner: str
    balance: float
    currency: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize Account to a JSON-friendly dict."""
        return {
            "id": self.id,
            "owner": self.owner,
            "balance": self.balance,
            "currency": self.currency,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Account":
        """Deserialize an Account from a dict created by to_dict."""
        return Account(
            id=str(data.get("id", "")),
            owner=str(data.get("owner", "")),
            balance=float(data.get("balance", 0.0)),
            currency=str(data.get("currency", "USD")),
            created_at=str(data.get("created_at", datetime.utcnow().isoformat())),
        )
