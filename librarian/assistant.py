from typing import List, Dict, Optional

from contextlib import AsyncExitStack

import os
import asyncio

import dspy
from fastmcp import Client


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
    def __init__(self, mcp_session: Client):
        super().__init__()

        self.mcp_session = mcp_session

    async def ainit(self):
        tools = await self.mcp_session.list_tools()
        dspy_tools = []
        for tool in tools.tools:
            dspy_tools.append(dspy.Tool.from_mcp_tool(self.mcp_session, tool))

        self.lm = dspy.ReAct(
            signature=LibrarianSignature,
            tools=dspy_tools,
        )

    async def call(self):
        return await self.mcp_session.call_tool(
            "add_book",
            {
                "book_id": "1",
                "title": "hello",
                "author": "will",
                "num_copies": 2,
            },
        )

    async def aforward(self, request: str):
        try:
            return await self.lm.acall(user_request=request)
        except Exception as e:
            print(f"Error calling LM agent: {e}")


async def main():
    agent = None
    try:
        async with Client("http://localhost:5400/mcp") as client:
            agent = LibrarianAgent(client.session)
            await agent.ainit()

            while True:
                request = input("Library > ")
                response = await agent.acall(request)
                print(response.process_result)
    except Exception as e:
        print(f"Error calling agent: {e}")
        if agent:
            print(agent.inspect_history())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled..")
