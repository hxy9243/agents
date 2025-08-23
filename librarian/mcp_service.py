from typing import List
import time


from pydantic import BaseModel, Field

from fastmcp import FastMCP, Context
from fastmcp.server.middleware import Middleware, MiddlewareContext
from starlette.exceptions import HTTPException

from librarian.library import Library, Book, Loan, Member


library = Library()
library.add_example_data()


mcp = FastMCP(
    "LibraryManagement",
)


@mcp.tool()
async def my_member_info(ctx: Context):
    """Get the user's member_id information"""

    return ctx.get_state("member_id")


@mcp.tool()
async def add_book(
    ctx: Context, book_id: str, title: str, author: str, num_copies: int = 1
):
    """Adds a new book and its copies to the library."""

    auth_id = ctx.get_state("member_id")
    print(f"Getting request to call add_book from member {auth_id}")

    library.add_book(book_id, title, author, num_copies)
    return {"message": f"Added {num_copies} copies of '{title}'."}


@mcp.tool()
async def search_member(ctx: Context, name: str) -> Member:
    """Gets library member by name."""

    auth_id = ctx.get_state("member_id")
    print(f"Getting request to call add_book from member {auth_id}")

    return library.search_member(name)


@mcp.tool()
async def borrow_book(ctx: Context, book_id: str, member_id: int) -> Loan:
    """Borrows a book for a member. Return detailed loan data information including load id and copy id"""
    auth_id = ctx.get_state("member_id")
    if auth_id != member_id:
        raise HTTPException(status_code=403, detail="Forbidden, unauthorized access")

    return library.borrow_book(book_id, member_id)


@mcp.tool()
async def return_book(ctx: Context, copy_id: int) -> Loan:
    """Returns a borrowed book copy."""
    auth_id = ctx.get_state("member_id")

    print(f"Getting request to call add_book from member {auth_id}")

    return library.return_book(copy_id)


@mcp.tool()
async def get_book(ctx: Context, book_id: str) -> Book:
    """Returns a borrowed book copy."""
    auth_id = ctx.get_state("member_id")

    print(f"Getting request to call get_book from member {auth_id}")

    return library.get_book(book_id)


@mcp.tool()
async def search_books(query: str) -> List[Book]:
    """Searches for books by title or author."""
    print("Getting request to call search books")

    return library.search_books(query)


@mcp.tool()
async def get_member_loans(ctx: Context, member_id: int) -> List[Loan]:
    """Gets all loans for a specific member."""
    auth_id = ctx.get_state("member_id")

    print(f"Getting request to find member loans: {auth_id}")

    if auth_id != 0 and auth_id != member_id:
        raise HTTPException(status_code=403, detail="Forbidden, unauthorized access")

    return library.get_member_loans(member_id)


class UserAuthMiddleware(Middleware):
    def _parse_token(self, context) -> str:
        headers = context.fastmcp_context.request_context.request.headers

        # parse authorization header
        bearer_token = headers.get("authorization")
        if not bearer_token:
            raise HTTPException(status_code=401, detail="Unauthorized")

        token = bearer_token.split(" ")[1]
        return token

    def _lookup_member(self, token) -> str:
        # Toy impl of an Auth token service, maps from token to member id
        # In reality this should be your Auth service
        tokens_to_members = {
            "token_000": 0,  # admin
            "token_001": 1,  # alice
            "token_002": 2,  # bob
            "token_003": 3,  # charlie
            "token_004": 4,  # diana
            "token_005": 5,  # eve
        }
        return tokens_to_members.get(token)

    async def on_call_tool(self, context, call_next):
        token = self._parse_token(context)
        member_id = self._lookup_member(token)
        print(
            f"Authorized connection from member {member_id}: {library.members[member_id]}"
        )

        # Authz for access to book
        admin_tools = [
            "add_book",
            "search_member",
        ]
        tool = context.message.name
        if member_id != 0 and tool in admin_tools:
            raise HTTPException(status_code=403, detail="Forbidden")

        context.fastmcp_context.set_state("member_id", member_id)
        return await call_next(context)


if __name__ == "__main__":
    mcp.add_middleware(UserAuthMiddleware())
    mcp.run("streamable-http", port=5400)
