import json
from typing import List, Dict, Any

# Predefined books in JSON format
BOOKS_JSON = '''
[
    {"id": 1, "title": "1984", "author": "George Orwell", "available": true},
    {"id": 2, "title": "The Catcher in the Rye", "author": "J.D. Salinger", "available": true},
    {"id": 3, "title": "To Kill a Mockingbird", "author": "Harper Lee", "available": true},
    {"id": 4, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "available": true}
]
'''  

class Library:
    def __init__(self) -> None:
        self.books = self.load_books()

    def load_books(self) -> List[Dict[str, Any]]:
        """Load books from JSON format."""
        try:
            return json.loads(BOOKS_JSON)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error loading books: {e}")

    def list_books(self) -> List[Dict[str, Any]]:
        """List all available books in the library."""
        return [book for book in self.books if book['available']]

    def borrow_book(self, book_id: int) -> str:
        """Borrow a book by its ID if available."""
        for book in self.books:
            if book['id'] == book_id:
                if book['available']:
                    book['available'] = False
                    return f"You have borrowed '{book['title']}'."
                return "Sorry, this book is not available."
        return "Book not found."

    def return_book(self, book_id: int) -> str:
        """Return a book by its ID."""
        for book in self.books:
            if book['id'] == book_id:
                book['available'] = True
                return f"You have returned '{book['title']}'."
        return "Book not found."

def main() -> None:
    library = Library()
    print("Available books:")
    for book in library.list_books():
        print(f"{book['id']}: {book['title']} by {book['author']}")

    # Simulate borrowing and returning books
    print(library.borrow_book(1))
    print(library.return_book(1))
    print(library.borrow_book(2))

if __name__ == '__main__':
    main()