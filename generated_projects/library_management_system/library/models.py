from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class User:
    """Represents a library user with an integer ID and a name."""
    id: int
    name: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the User to a plain dictionary."""
        return {"id": self.id, "name": self.name}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "User":
        """Deserialize a User from a dictionary."""
        return User(id=int(data["id"]), name=str(data["name"]))


@dataclass
class Book:
    """Represents a book with id, title, author, total copies and available copies."""
    id: int
    title: str
    author: str
    copies_total: int
    copies_available: int

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Book to a plain dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "copies_total": self.copies_total,
            "copies_available": self.copies_available,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Book":
        """Deserialize a Book from a dictionary."""
        return Book(
            id=int(data["id"]),
            title=str(data["title"]),
            author=str(data["author"]),
            copies_total=int(data.get("copies_total", 0)),
            copies_available=int(data.get("copies_available", 0)),
        )
