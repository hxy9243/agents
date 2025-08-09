from typing import List
import time


from pydantic import BaseModel, Field

from mcp.server.auth.provider import TokenVerifier, AccessToken
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.auth.settings import AuthSettings

import mcpauth
from mcpauth import MCPAuth
from mcpauth.config import AuthServerType, AuthServerConfig, AuthorizationServerMetadata
from mcpauth.utils import fetch_server_config, fetch_server_config_by_well_known_url
from mcpauth.types import AuthInfo

from starlette.applications import Starlette
from starlette.routing import Mount
from starlette.middleware import Middleware

from librarian.library import Library, Book, Loan, Member

library = Library()

# Populate with some data


class NaiveTokenVerifier(TokenVerifier):
    async def verify_token(self, token: str) -> AccessToken:
        print("Hello world")

        return AccessToken(
            token=token,
            client_id="tom",
            scopes=["read", "write"],
            expires_at=int(time.time() + 3600 * 24),
            resource="library",
        )


mcp = FastMCP(
    "LibraryManagement",
    port=5400,
    # mount_path="/see",
    token_verifier=NaiveTokenVerifier(),
    auth=AuthSettings(
        issuer_url="http://example.com",
        required_scopes=["read"],
        resource_server_url="http://localhost",
    ),
)


def validate_token(token: str) -> AuthInfo:
    """Validates the token and returns auth info."""
    print(f"Validating token: {token}")

    # Here you would implement your token validation logic
    # For now, we return a dummy AuthInfo object
    return AuthInfo(
        client_id="bob",
        subject="bob",
        scopes=["user"],
        token=token,
        issuer="https://accounts.google.com",
        claims={"username": "bob"},
    )


auth_server_config = fetch_server_config_by_well_known_url(
    well_known_url="https://accounts.google.com/.well-known/openid-configuration",
    type=AuthServerType.OAUTH,
)
mcp_auth = MCPAuth(server=auth_server_config)
bearer_auth_middleware = mcp_auth.bearer_auth_middleware(validate_token)


@mcp.tool()
async def add_book(
    ctx: Context, book_id: str, title: str, author: str, num_copies: int = 1
):
    """Adds a new book and its copies to the library."""

    print(f"Getting request to call add_book from client {ctx.client_id}, ctx: {ctx}")
    library.add_book(book_id, title, author, num_copies)
    return {"message": f"Added {num_copies} copies of '{title}'."}


@mcp.tool()
async def borrow_book(book_id: str, member_id: int) -> Loan:
    """Borrows a book for a member. Return detailed loan data information including load id and copy id"""
    ctx = mcp.get_context()
    print(
        f"Getting request to call borrow_book from client {ctx.client_id}, ctx: {ctx}"
    )
    return library.borrow_book(book_id, member_id)


@mcp.tool()
async def return_book(copy_id: int) -> Loan:
    """Returns a borrowed book copy."""
    ctx = mcp.get_context()

    print(
        f"Getting request to call return_book from client {ctx.client_id}, ctx: {ctx}"
    )

    return library.return_book(copy_id)


@mcp.tool()
async def search(query: str) -> List[Book]:
    """Searches for books by title or author."""
    print(f"Getting request to call search from client ")

    print("claims", mcp_auth.auth_info)

    print("claims", mcp_auth.auth_info.claims)

    return library.search_books(query)


@mcp.tool()
async def search_member(member: str) -> List[Member]:
    """Gets members of the library."""
    ctx = mcp.get_context()

    print(f"Getting request to call search member from client {ctx.client_id}")

    print("claims", mcp_auth.auth_info)

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


# mcp.run(transport="streamable-http")
# def create_app():
#     from mcpauth.config import (
#         AuthServerConfig,
#         AuthServerType,
#         AuthorizationServerMetadata,
#     )

#     app = Starlette(
#         routes=[
#             mcp_auth.metadata_route(),
#             Mount(
#                 "/",
#                 app=mcp.sse_app(),
#             ),
#         ],
#     )
#     return app


# app = create_app()


mcp.run(mount_path="/mcp", transport="streamable-http")