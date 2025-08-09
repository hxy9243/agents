from typing import List
import time

from pydantic import BaseModel, Field

from mcp.server.fastmcp import FastMCP, Context

from librarian.library import Library, Book, Loan, Member, add_example_data

library = Library()

add_example_data(library)


mcp = FastMCP(
    "LibraryManagement",
    port=5400,
)


@mcp.tool()
async def add_book(book_id: str, title: str, author: str, num_copies: int = 1):
    """Adds a new book and its copies to the library."""
    library.add_book(book_id, title, author, num_copies)
    return {"message": f"Added {num_copies} copies of '{title}'."}


@mcp.tool()
async def borrow_book(book_id: str, member_id: int) -> Loan:
    """Borrows a book for a member. Return detailed loan data information including load id and copy id"""
    return library.borrow_book(book_id, member_id)


@mcp.tool()
async def return_book(copy_id: int) -> Loan:
    """Returns a borrowed book copy."""
    return library.return_book(copy_id)


@mcp.tool()
async def search(query: str) -> list[Book]:
    """Searches for books by title or author."""
    print(f"Getting request to call search from client ")
    return library.search_books(query)


@mcp.tool()
async def search_member(member: str) -> List[Member]:
    """Gets members of the library."""
    return list(library.members.values())


@mcp.resource("books://")
async def get_all_books() -> List[Book]:
    """Gets all books in the library."""
    return list(library.books.values())


@mcp.resource("members://")
async def get_all_members() -> List[Member]:
    """Gets all members of the library."""
    return list(library.members.values())


@mcp.resource("loans://member/{member_id}")
async def get_member_loans(member_id: int) -> List[Loan]:
    """Gets all loans for a specific member."""
    return library.get_member_loans(member_id)


mcp.run(transport="streamable-http")
