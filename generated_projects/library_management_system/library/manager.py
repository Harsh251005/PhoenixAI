from typing import List, Optional

from .models import User, Book
from .storage import JSONStorage


class LibraryManager:
    """High-level operations for managing users, books and loans persisted to JSON files."""

    def __init__(self, base_dir: str) -> None:
        """Initialize JSONStorage instances for users, books and loans using the provided base directory."""
        self.users_store = JSONStorage("users.json", base_dir)
        self.books_store = JSONStorage("books.json", base_dir)
        self.loans_store = JSONStorage("loans.json", base_dir)

    # Helper read/write converters
    def _load_users(self) -> List[User]:
        """Load and return all users from storage."""
        raw = self.users_store.read_all()
        return [User.from_dict(d) for d in raw]

    def _save_users(self, users: List[User]) -> None:
        """Persist the provided list of User objects to storage."""
        self.users_store.save_all([u.to_dict() for u in users])

    def _load_books(self) -> List[Book]:
        """Load and return all books from storage."""
        raw = self.books_store.read_all()
        return [Book.from_dict(d) for d in raw]

    def _save_books(self, books: List[Book]) -> None:
        """Persist the provided list of Book objects to storage."""
        self.books_store.save_all([b.to_dict() for b in books])

    def _load_loans(self) -> List[dict]:
        """Load and return loan records from storage. Each loan is a dict with 'user_id' and 'book_id'."""
        return self.loans_store.read_all()

    def _save_loans(self, loans: List[dict]) -> None:
        """Persist the provided list of loan records to storage."""
        self.loans_store.save_all(loans)

    # Public operations
    def add_user(self, name: str) -> User:
        """Create and persist a new user with an auto-incremented integer ID."""
        if not name:
            raise ValueError("User name cannot be empty.")
        users = self._load_users()
        next_id = 1 + max((u.id for u in users), default=0)
        user = User(id=next_id, name=name)
        users.append(user)
        self._save_users(users)
        return user

    def add_book(self, title: str, author: str, copies: int) -> Book:
        """Create and persist a new book with copies (must be positive)."""
        if not title or not author:
            raise ValueError("Title and author are required.")
        if copies <= 0:
            raise ValueError("Copies must be a positive integer.")
        books = self._load_books()
        next_id = 1 + max((b.id for b in books), default=0)
        book = Book(id=next_id, title=title, author=author, copies_total=copies, copies_available=copies)
        books.append(book)
        self._save_books(books)
        return book

    def list_books(self) -> List[Book]:
        """Return a list of all books currently persisted."""
        return self._load_books()

    def list_users(self) -> List[User]:
        """Return a list of all users currently persisted."""
        return self._load_users()

    def _find_book(self, book_id: int) -> Optional[Book]:
        """Find a book by its integer ID or return None if not found."""
        for b in self._load_books():
            if b.id == book_id:
                return b
        return None

    def _find_user(self, user_id: int) -> Optional[User]:
        """Find a user by its integer ID or return None if not found."""
        for u in self._load_users():
            if u.id == user_id:
                return u
        return None

    def borrow_book(self, user_id: int, book_id: int) -> str:
        """Attempt to borrow a book for a user; returns a status message describing the outcome."""
        user = self._find_user(user_id)
        if user is None:
            return f"User with ID {user_id} does not exist."
        books = self._load_books()
        book = next((b for b in books if b.id == book_id), None)
        if book is None:
            return f"Book with ID {book_id} does not exist."
        if book.copies_available <= 0:
            return f"No available copies of '{book.title}'."
        loans = self._load_loans()
        if any(l.get("user_id") == user_id and l.get("book_id") == book_id for l in loans):
            return f"User {user_id} already borrowed book {book_id}."
        # Perform borrow
        book.copies_available -= 1
        # Save updated books
        self._save_books(books)
        loans.append({"user_id": user_id, "book_id": book_id})
        self._save_loans(loans)
        return f"Book '{book.title}' borrowed successfully by {user.name}."

    def return_book(self, user_id: int, book_id: int) -> str:
        """Attempt to return a borrowed book for a user; returns a status message describing the outcome."""
        user = self._find_user(user_id)
        if user is None:
            return f"User with ID {user_id} does not exist."
        books = self._load_books()
        book = next((b for b in books if b.id == book_id), None)
        if book is None:
            return f"Book with ID {book_id} does not exist."
        loans = self._load_loans()
        loan_index = next((i for i, l in enumerate(loans) if l.get("user_id") == user_id and l.get("book_id") == book_id), None)
        if loan_index is None:
            return f"No existing loan found for user {user_id} and book {book_id}."
        # Perform return
        del loans[loan_index]
        self._save_loans(loans)
        # Increase available copies but do not exceed total
        for b in books:
            if b.id == book_id:
                b.copies_available = min(b.copies_total, b.copies_available + 1)
                break
        self._save_books(books)
        return f"Book '{book.title}' returned successfully by {user.name}."
