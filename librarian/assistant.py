from typing import List, Dict, Optional

import os
import asyncio

import dspy
from fastmcp import Client
from mcp import ClientSession
from fastmcp.client.transports import StreamableHttpTransport


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

    You can lookup users's information by calling .

    You can use search book function to find books.

    When user is borrowing books, you should return the book info and copy id.

    If users' request doesn't pertain to library or books, simply decline politely.

    If user's request returns 401 or 403, politely inform them they're not authorized to
    access that information.
    """

    history: dspy.History = dspy.InputField(desc="conversation history")
    user_request: str = dspy.InputField(desc="user input request")
    process_result: str = dspy.OutputField(
        desc=(
            "Message that summarizes the process result, and the information users need"
        )
    )


class LibrarianAgent(dspy.Module):
    def __init__(self, mcp_session: ClientSession):
        super().__init__()

        self.mcp_session = mcp_session
        self.conversations = dspy.History(messages=[])

    async def ainit(self):
        dspy_tools = []

        tools = await self.mcp_session.list_tools()
        for tool in tools.tools:
            dspy_tools.append(dspy.Tool.from_mcp_tool(self.mcp_session, tool))

        self.lm = dspy.ReAct(
            signature=LibrarianSignature,
            tools=dspy_tools,
        )

    async def aforward(self, request: str):
        try:
            resp = await self.lm.acall(history=self.conversations, user_request=request)
            print(resp.process_result)
            self.conversations.messages.append(
                {"request": request, **resp}
            )
            return resp

        except Exception as e:
            print(f"Error calling LM agent: {e}")
            raise e


async def main():
    token = os.environ.get("TEST_TOKEN")
    if not token:
        raise ValueError("Your user token not set")

    try:
        transport = StreamableHttpTransport(
            url="http://localhost:5400/mcp",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

        async with Client(transport) as client:
            agent = LibrarianAgent(client.session)
            await agent.ainit()

            member = await client.call_tool("my_member_info")
            if member.is_error:
                raise ValueError("Error: unable to login")

            print(f"Welcome, user {member.data.name}")

            while True:
                request = input("Library > ")
                response = await agent.acall(request)
                print(response)

    except Exception as e:
        print(f"Error calling agent: {e}")
        raise e


if __name__ == "__main__":
    asyncio.run(main())
