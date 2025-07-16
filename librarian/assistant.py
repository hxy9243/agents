from typing import List, Dict

import os
import asyncio
from contextlib import AsyncExitStack

import dspy
from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client


lm = dspy.LM(
    model=os.getenv("LM_MODEL_NAME", "gemini/gemini-2.5-flash"),
    api_base=os.getenv("LM_BASE_URL", None),
    api_key=os.getenv("LM_API_KEY"),
    max_tokens=16384,
)


dspy.configure(lm=lm, track_usage=False)


class LibrarianSignature(dspy.Signature):
    """You are a librarian. You are given a list of tools to handle user requests.
    You should decide the right tool to use in order to fulfill users' requests.

    You can lookup users's information by searching members.

    You can use search book function to find books.

    When user is borrowing books, you should return the book info and copy id.

    If users' request doesn't pertain to library or books, simply decline politely.
    """

    user_request: str = dspy.InputField()
    process_result: str = dspy.OutputField(
        desc=(
            "Message that summarizes the process result, and the information users need"
        )
    )


class LibrarianAgent(dspy.Module):
    def __init__(self, mcp_address: str):
        super().__init__()
        self.mcp_address = mcp_address
        self.lm = None  # Initialize lm to None, will be set in ainit

        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def aclose(self):
        await self.exit_stack.aclose()

    async def ainit(self):
        """Asynchronous initialization method to connect to MCP and set up the LM."""
        tools = await self.connect_mcp(self.mcp_address)

        self.lm = dspy.ReAct(
            signature=LibrarianSignature,
            tools=tools,
        )
        return self

    async def connect_mcp(self, mcp_address: str) -> List[dspy.Tool]:
        # Initialize the connection
        read, write = await self.exit_stack.enter_async_context(
            sse_client(mcp_address, headers={'authorization': 'bearer 12345'}),
        )
        session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        # Convert MCP tools to DSPy tools
        tools = await session.list_tools()
        dspy_tools = []
        for tool in tools.tools:
            dspy_tools.append(dspy.Tool.from_mcp_tool(session, tool))

        return dspy_tools

    async def aforward(self, request: str):
        if self.lm is None:
            raise RuntimeError(
                "LibrarianAgent not initialized. Call await agent.ainit() first."
            )
        tools = await self.connect_mcp(self.mcp_address)
        try:
            self.lm = dspy.ReAct(
                signature=LibrarianSignature,
                tools=tools,
            )

            return await self.lm.acall(user_request=request)
        except Exception as e:
            print(f"Error calling LM agent: {e}")


if __name__ == "__main__":

    async def main():
        try:
            agent = LibrarianAgent("http://localhost:5400/sse")
            await agent.ainit()  # Call the asynchronous initialization
            response = await agent.acall(
                "hello, I'm bob. What books do you have?",
            )
            print(response)
        finally:
            await agent.aclose()


asyncio.run(main())
