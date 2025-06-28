import dspy

from mcp import ClientSession, StdioServerParameters
#from mcp.client.
# from mcp.client.streamable_http import streamablehttp_client
from mcp.client.streamable_http import streamablehttp_client

# from mcp.client.stdio import stdio_client

# # Create server parameters for stdio connection
# server_params = StdioServerParameters(
#     command="python",  # Executable
#     args=["path_to_your_working_directory/mcp_server.py"],
#     env=None,
# )

async def run():
    async with streamablehttp_client("http://localhost:5400/mcp") as (read, write, _):
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

if __name__ == "__main__":
    import asyncio

    asyncio.run(run())