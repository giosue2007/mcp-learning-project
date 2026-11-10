#!/usr/bin/env python3
"""
Agent-like client: answers a student question using only the data
returned by the Programming Learning Server, called through MCP.

Usage:
    python3 client/agent.py "I want to study Python decorators."
"""
import asyncio
import re
import sys
from pathlib import Path

from fastmcp import Client

ROOT = Path(__file__).parent.parent
SERVER = ROOT / "server" / "learning_server.py"
OUTPUT = ROOT / "output" / "sample_agent_response.md"
STOP_WORDS = {"want", "study", "what", "should", "review", "first",
              "learn", "about", "with", "how", "the", "and", "for"}


def keywords(question):
    """
    Return the useful words of the question (lowercase, no stop words).
    """
    words = re.findall(r"[a-z0-9]+", question.lower())
    return [word for word in words
            if len(word) > 2 and word not in STOP_WORDS]


async def find_best_topic(client, question):
    """
    Call search_topics (through MCP) for each keyword and return
    the topic found most often, with the words that matched it.
    """
    scores = {}
    for word in keywords(question):
        result = await client.call_tool("search_topics", {"query": word})
        for topic in result.data:
            entry = scores.setdefault(topic["id"], [topic, []])
            entry[1].append(word)
    if not scores:
        return None, []
    return max(scores.values(), key=lambda entry: len(entry[1]))


def bullets(items):
    """
    Turn a list into Markdown bullet lines.
    """
    return "\n".join(f"- {item}" for item in items)


def format_answer(question, details, matched):
    """
    Build the student-facing Markdown answer from the MCP data.
    """
    if details is None:
        return (f"# Study Assistant\n\n**Question:** {question}\n\n"
                "No matching topic was found in the catalog. "
                "Try another keyword.\n")
    return (
        f"# Study Assistant\n\n**Question:** {question}\n\n"
        f"## Recommended topic\n\n{details['title']}\n\n"
        f"## Why it is relevant\n\nYour question mentions "
        f"{', '.join(matched)}. {details['summary']}\n\n"
        f"## Prerequisites\n\n{bullets(details['prerequisites'])}\n\n"
        f"## Key concepts\n\n{bullets(details['key_concepts'])}\n\n"
        f"## Practice idea\n\n{details['practice_idea']}\n\n"
        f"## Common mistakes to avoid\n\n"
        f"{bullets(details['common_mistakes'])}\n"
    )


async def answer(question):
    """
    Connect to the MCP server, find a topic, get its details
    and return the Markdown answer.
    """
    async with Client(SERVER) as client:
        topic, matched = await find_best_topic(client, question)
        details = None
        if topic is not None:
            result = await client.call_tool(
                "get_topic_details", {"topic_id": topic["id"]})
            details = result.data
    return format_answer(question, details, matched)


def main():
    """
    Read the question, print the answer and save it in output/.
    """
    question = " ".join(sys.argv[1:]).strip() or (
        "I want to study Python decorators. What should I review first?")
    text = asyncio.run(answer(question))
    print(text)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"Saved to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
