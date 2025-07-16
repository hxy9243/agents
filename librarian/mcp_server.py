from typing import List

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


mcp = FastMCP(
    "LibraryManagement",
    port=5400,
    path="/mcp",
    # token_verifier=NaiveTokenVerifier(),
    # auth=AuthSettings(
    #     issuer_url="http://example.com",
    #     required_scopes=["user"],
    #     resource_server_url="http://localhost",
    # ),
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
auth = MCPAuth(server=auth_server_config)
bearer_auth_middleware = auth.bearer_auth_middleware(validate_token)



@mcp.tool()
async def add_book(book_id: str, title: str, author: str, num_copies: int = 1):
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

    breakpoint()

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

    print("claims", auth.auth_info)

    print("claims", auth.auth_info.claims)

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
def create_app():
    from mcpauth.config import (
        AuthServerConfig,
        AuthServerType,
        AuthorizationServerMetadata,
    )

    # mcp_auth = MCPAuth(
    #     server=AuthServerConfig(
    #         type=AuthServerType.OIDC,  # or AuthServerType.OAUTH
    #         metadata=AuthorizationServerMetadata(
    #             issuer='https://accounts.google.com',
    #             authorization_endpoint='https://accounts.google.com/o/oauth2/v2/auth',
    #             # ... other metadata fields
    #         ),
    #     )
    # )

    # auth_issuer = ' https://accounts.google.com/'
    # auth_server_config = fetch_server_config_by_well_known_url(
    #     well_known_url="https://accounts.google.com/.well-known/openid-configuration",
    #     type=AuthServerType.OAUTH,
    # )
    # auth = MCPAuth(server=auth_server_config)

    # bearer_auth_middleware = auth.bearer_auth_middleware(validate_token)

    app = Starlette(
        routes=[
            auth.metadata_route(),
            Mount(
                "/",
                app=mcp.sse_app(),
                middleware=[Middleware(bearer_auth_middleware)],
            ),
        ],
    )

    return app


app = create_app()
