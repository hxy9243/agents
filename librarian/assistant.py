from typing import List, Dict

import os
import asyncio

import dspy


from mcp import ClientSession, StdioServerParameters

# from mcp.client.
# from mcp.client.streamable_http import streamablehttp_client
from mcp.client.streamable_http import streamablehttp_client

# from mcp.client.stdio import stdio_client

# # Create server parameters for stdio connection
# server_params = StdioServerParameters(
#     command="python",  # Executable
#     args=["path_to_your_working_directory/mcp_server.py"],
#     env=None,
# )

# dspy.configure(lm=dspy.LM("openai/gpt-4o-mini"))

lm = dspy.LM(
    model=os.getenv("LM_MODEL_NAME", "gemini/gemini-2.0-flash"),
    api_key=os.getenv("LM_API_KEY"),
    max_tokens=16384,
)


dspy.configure(lm=lm, track_usage=False)


class LibrarianSignature(dspy.Signature):
    """You are a librarian. You are given a list of tools to handle user requests.
    You should decide the right tool to use in order to fulfill users' requests.

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
        self.lm = None # Initialize lm to None, will be set in ainit

    async def ainit(self):
        """Asynchronous initialization method to connect to MCP and set up the LM."""
        tools = await self.connect_mcp(self.mcp_address)
        self.lm = dspy.ReAct(
            signature=LibrarianSignature,
            tools=tools,
        )
        return self # Return self to allow chaining in the factory method

    async def connect_mcp(self, mcp_address: str) -> List[dspy.Tool]:
        async with streamablehttp_client(mcp_address) as (read, write, _):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                # List available tools
                tools = await session.list_tools()

                # Convert MCP tools to DSPy tools
                dspy_tools = []
                for tool in tools.tools:
                    dspy_tools.append(dspy.Tool.from_mcp_tool(session, tool))

                print(len(dspy_tools))
                for tool in dspy_tools:
                    print(tool.name)
                    print(tool.args)

                return dspy_tools

    async def aforward(self, request: str):
        if self.lm is None:
            raise RuntimeError("LibrarianAgent not initialized. Call await agent.ainit() first.")
        return self.lm(user_request=request) # Changed to explicitly pass as keyword argument


if __name__ == "__main__":
    async def main():
        agent = LibrarianAgent("http://localhost:5400/mcp")
        await agent.ainit() # Call the asynchronous initialization
        response = await agent.aforward("hello, what books do you have?")
        print(response)

    asyncio.run(main())
