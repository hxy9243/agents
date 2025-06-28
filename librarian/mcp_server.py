from typing import List
from mcp.server.fastmcp import FastMCP
from librarian.library import Library, Book, Loan, Member

mcp = FastMCP("LibraryManagement", port=5400, path='/mcp')
library = Library()

# Populate with some data
library.add_book(
    "978-0345391803", "The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 3
)
library.add_book("978-0618640157", "The Lord of the Rings", "J.R.R. Tolkien", 2)
library.add_book("978-0743273565", "The Da Vinci Code", "Dan Brown", 5)
library.add_book("978-0439023528", "The Hunger Games", "Suzanne Collins", 4)
library.add_book("978-0385537858", "The Martian", "Andy Weir", 3)
library.add_book("978-1451673319", "Fahrenheit 451", "Ray Bradbury", 2)
library.add_book("978-0743273565", "To Kill a Mockingbird", "Harper Lee", 4)
library.add_book("978-0452284234", "1984", "George Orwell", 3)
library.add_book("978-0743273565", "The Great Gatsby", "F. Scott Fitzgerald", 2)
library.add_book("978-0142437230", "The Catcher in the Rye", "J.D. Salinger", 1)
library.add_book(
    "978-0307474278", "The Girl with the Dragon Tattoo", "Stieg Larsson", 3
)
library.add_book("978-0316067938", "The Road", "Cormac McCarthy", 2)
library.add_book("978-0743273565", "Brave New World", "Aldous Huxley", 2)
library.add_book("978-0446310789", "To Kill a Mockingbird", "Harper Lee", 3)
library.add_book("978-0679783268", "Pride and Prejudice", "Jane Austen", 4)
library.add_book("978-0061120084", "The Alchemist", "Paulo Coelho", 5)
library.add_book("978-0307277671", "The Kite Runner", "Khaled Hosseini", 3)
library.add_book("978-1400033423", "The Secret History", "Donna Tartt", 2)
library.add_book("978-0307387899", "Gone Girl", "Gillian Flynn", 4)
library.add_book("978-0553380033", "A Brief History of Time", "Stephen Hawking", 2)
library.add_member("Alice", "alice@example.com")
library.add_member("Bob", "bob@example.com")
library.add_member("Charlie", "charlie@example.com")
library.add_member("Diana", "diana@example.com")
library.add_member("Eve", "eve@example.com")


@mcp.tool()
def add_book(book_id: str, title: str, author: str, num_copies: int = 1):
    """Adds a new book and its copies to the library."""
    library.add_book(book_id, title, author, num_copies)
    return {"message": f"Added {num_copies} copies of '{title}'."}


@mcp.tool()
def borrow_book(book_id: str, member_id: int) -> Loan:
    """Borrows a book for a member."""
    return library.borrow_book(book_id, member_id)


@mcp.tool()
def return_book(copy_id: int) -> Loan:
    """Returns a borrowed book copy."""
    return library.return_book(copy_id)


@mcp.tool()
def search(query: str) -> List[Book]:
    """Searches for books by title or author."""
    return library.search_books(query)


@mcp.resource("books://")
def get_all_books() -> List[Book]:
    """Gets all books in the library."""
    return list(library.books.values())


@mcp.resource("members://")
def get_all_members() -> List[Member]:
    """Gets all members of the library."""
    return list(library.members.values())


@mcp.resource("loans://member/{member_id}")
def get_member_loans(member_id: int) -> List[Loan]:
    """Gets all loans for a specific member."""
    return library.get_member_loans(member_id)


mcp.run(transport="streamable-http")
