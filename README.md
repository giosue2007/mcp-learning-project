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

## Testing the Server

Run `python3 client/mcp_client.py`. Sample output:

    1. Server started and connected.
    2. Tools: ['search_topics', 'get_topic_details']
    3. search_topics('decorators'): [{'id': 'python-decorators', ...}]
    6. Invalid inputs:
       get_topic_details('unknown'): Topic 'unknown' not found.

## Third-Party MCP Server Review

**Server reviewed:** Filesystem MCP Server
(`@modelcontextprotocol/server-filesystem`), a reference server from
the official `modelcontextprotocol/servers` repository. I reviewed
its README and configuration examples; I did not install it.

**What it does:** lets an AI application read, write, search and
organize files inside directories chosen by the user.

**Local or remote:** local. The client starts it as a subprocess
(`npx` or `docker run -i`) and talks to it over stdio. No network
endpoint is exposed.

**Tools exposed:** `read_text_file`, `read_media_file`,
`read_multiple_files`, `write_file`, `edit_file`,
`create_directory`, `list_directory`, `list_directory_with_sizes`,
`move_file`, `search_files`, `directory_tree`, `get_file_info`,
`list_allowed_directories`.

**Permissions / credentials:** no API key or account. The only
permission is file-system access: the allowed directories are given
as command-line arguments (or as MCP roots by the client). Every
operation is restricted to those directories.

**Risk:** `write_file`, `edit_file` and `move_file` can overwrite or
move files without asking. If I allowed a broad folder (for example
my home directory), a wrong or manipulated request from the AI could
damage personal files or read private ones.

**Safety measure:** allow only one small project folder, never the
home directory. With Docker, mount it read-only (`ro`) when the AI
only needs to read, for example only this project's `data/` folder.
Use `edit_file` with `dryRun` to preview changes before writing.
