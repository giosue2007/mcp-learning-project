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


@mcp.tool
def get_topic_details(topic_id: str) -> dict:
    """
    Return the full information of one topic, found by its id.
    If the id does not exist, return an error message and the
    list of valid ids.
    """
    topic_id = str(topic_id).strip().lower()
    topics = load_topics()
    for topic in topics:
        if topic["id"] == topic_id:
            return topic
    return {
        "error": f"Topic '{topic_id}' not found.",
        "available_ids": [topic["id"] for topic in topics],
    }


@mcp.resource("topics://catalog")
def get_topic_catalog() -> str:
    """
    Read-only catalog: the id and title of every available topic,
    as a JSON string.
    """
    catalog = [
        {"id": topic["id"], "title": topic["title"]}
        for topic in load_topics()
    ]
    return json.dumps(catalog, indent=2)


if __name__ == "__main__":
    mcp.run()
