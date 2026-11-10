#!/usr/bin/env python3
"""
Programming Learning Server: a minimal MCP server built with FastMCP.
"""
from fastmcp import FastMCP

mcp = FastMCP("Programming Learning Server")


if __name__ == "__main__":
    mcp.run()
