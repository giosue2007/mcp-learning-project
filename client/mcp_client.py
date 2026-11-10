#!/usr/bin/env python3
"""
Small FastMCP client that tests the Programming Learning Server.

Usage:
    python3 client/mcp_client.py
"""
import asyncio
from pathlib import Path

from fastmcp import Client

SERVER = Path(__file__).parent.parent / "server" / "learning_server.py"


async def main():
    """
    Start the server (stdio), then test every tool and the resource.
    """
    async with Client(SERVER) as client:
        print("1. Server started and connected.")

        tools = await client.list_tools()
        print("2. Tools:", [tool.name for tool in tools])

        result = await client.call_tool(
            "search_topics", {"query": "decorators"})
        print("3. search_topics('decorators'):", result.data)

        result = await client.call_tool(
            "get_topic_details", {"topic_id": "python-decorators"})
        print("4. get_topic_details('python-decorators'):",
              result.data["title"], "-", result.data["summary"])

        content = await client.read_resource("topics://catalog")
        print("5. topics://catalog:")
        print(content[0].text)

        print("6. Invalid inputs:")
        result = await client.call_tool(
            "search_topics", {"query": "javascript"})
        print("   search_topics('javascript'):", result.data)
        result = await client.call_tool(
            "get_topic_details", {"topic_id": "unknown"})
        print("   get_topic_details('unknown'):", result.data["error"])


if __name__ == "__main__":
    asyncio.run(main())
