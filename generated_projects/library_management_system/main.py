import os
from typing import List

from library.manager import LibraryManager
from library.models import Book, User


def prompt_choice() -> str:
    """Prompt the user for a menu choice and return the raw input string."""
    print("\nLibrary Management System")
    print("1) Add user")
    print("2) Add book")
    print("3) List books")
    print("4) List users")
    print("5) Borrow book")
    print("6) Return book")
    print("7) Exit")
    return input("Choose an option (1-7): ").strip()


def main() -> None:
    """Create manager and run the interactive menu loop until the user exits."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    manager = LibraryManager(base_dir=base_dir)

    while True:
        choice = prompt_choice()
        if choice == "1":
            name = input("Enter user name: ").strip()
            try:
                user = manager.add_user(name)
                print(f"User added: ID={user.id}, Name={user.name}")
            except ValueError as exc:
                print(f"Error adding user: {exc}")
        elif choice == "2":
            title = input("Enter book title: ").strip()
            author = input("Enter book author: ").strip()
            copies_raw = input("Enter number of copies: ").strip()
            try:
                copies = int(copies_raw)
                book = manager.add_book(title=title, author=author, copies=copies)
                print(f"Book added: ID={book.id}, Title=\"{book.title}\", Copies={book.copies_total}")
            except ValueError:
                print("Number of copies must be a positive integer.")
        elif choice == "3":
            books = manager.list_books()
            if not books:
                print("No books available.")
            else:
                print("\nBooks:")
                for b in books:
                    print(f"ID={b.id} | Title=\"{b.title}\" | Author={b.author} | Available={b.copies_available}/{b.copies_total}")
        elif choice == "4":
            users = manager.list_users()
            if not users:
                print("No users registered.")
            else:
                print("\nUsers:")
                for u in users:
                    print(f"ID={u.id} | Name={u.name}")
        elif choice == "5":
            uid_raw = input("Enter user ID: ").strip()
            bid_raw = input("Enter book ID: ").strip()
            try:
                uid = int(uid_raw)
                bid = int(bid_raw)
                message = manager.borrow_book(user_id=uid, book_id=bid)
                print(message)
            except ValueError:
                print("User ID and Book ID must be integers.")
        elif choice == "6":
            uid_raw = input("Enter user ID: ").strip()
            bid_raw = input("Enter book ID: ").strip()
            try:
                uid = int(uid_raw)
                bid = int(bid_raw)
                message = manager.return_book(user_id=uid, book_id=bid)
                print(message)
            except ValueError:
                print("User ID and Book ID must be integers.")
        elif choice == "7" or choice.lower() == "exit":
            print("Exiting. Goodbye.")
            break
        else:
            print("Invalid choice, please select 1-7.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # broad catch to present a user-friendly message
        print(f"An unexpected error occurred: {exc}")
