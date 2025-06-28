from typing import List, Optional, Dict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LibraryManagement")
library = Library()

# Populate with some data
library.add_book("978-0345391803", "The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 3)
library.add_book("978-0618640157", "The Lord of the Rings", "J.R.R. Tolkien", 2)
library.add_member("Alice", "alice@example.com")
library.add_member("Bob", "bob@example.com")


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
