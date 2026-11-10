# MCP Learning Project

## MCP Architecture Summary

**MCP (Model Context Protocol)** is a standard way for an AI
application to use external capabilities (data, actions) through
a common protocol, instead of custom code for each integration.

- **MCP host**: the AI application the user interacts with
  (here, our agent). It manages the conversation and decides
  when to use an external capability.
- **MCP client**: a connector inside the host. It talks to one
  MCP server. A host connected to two servers has two clients.
- **MCP server**: a separate program that exposes capabilities.
  Here, `learning_server.py` exposes our learning topics.
- **Tools**: actions the server can run when asked, with inputs
  and a result (for example `get_topic("decorators")`).
- **Resources**: data the server makes available to read (for
  example the list of topics in `data/topics.json`).

**Example:** the agent (host) needs information about "Python
decorators". Its MCP client asks the learning server, the server
reads `topics.json` and returns the topic. The agent then uses it
in its answer.

**Least privilege:** a server should expose only what it really
needs. Fewer capabilities means fewer ways to misuse it (for
example, a learning server should read topics, not delete files),
and a smaller, easier to test server.

## How to Run the Server
1. Create and activate a virtual environment: `python3 -m venv .venv` then `source .venv/bin/activate`
2. Install the dependencies: `pip install -r requirements.txt`

The server uses the stdio transport: after the FastMCP banner it waits silently for a client. Stop it with Ctrl + C.
