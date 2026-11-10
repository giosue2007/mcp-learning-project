#!/usr/bin/env python3
"""
Programming Learning Server: an MCP server built with FastMCP
that exposes a small local dataset of programming topics.
"""
import json
from pathlib import Path

from fastmcp import FastMCP

DATA_FILE = Path(__file__).parent.parent / "data" / "topics.json"

mcp = FastMCP("Programming Learning Server")


def load_topics():
    """
    Read and return the list of topics from data/topics.json.
    """
    with open(DATA_FILE, encoding="utf-8") as file:
        return json.load(file)


@mcp.tool
def search_topics(query: str) -> list[dict]:
    """
    Search programming topics by title or key concept.
    Return the id, title and summary of each matching topic,
    or an empty list if nothing matches.
    """
    words = query.lower().split()
    if not words:
        return []

    results = []
    for topic in load_topics():
        text = " ".join([topic["title"]] + topic["key_concepts"]).lower()
        if all(word in text for word in words):
            results.append({
                "id": topic["id"],
                "title": topic["title"],
                "summary": topic["summary"],
            })
    return results


if __name__ == "__main__":
    mcp.run()
