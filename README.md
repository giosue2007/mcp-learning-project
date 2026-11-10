# MCP Servers in Python

## Description

A small **MCP server** written with FastMCP that exposes a local
dataset of programming topics, and a simple **agent-like client** that
uses this server through MCP to answer a student question.

    client/agent.py  ->  MCP client  ->  server/learning_server.py
                                          -> data/topics.json

## MCP Architecture Summary

**MCP (Model Context Protocol)** is a standard way for an AI
application to use external capabilities (data, actions) through a
common protocol, instead of custom code for each integration.

- **MCP host**: the AI application the user interacts with (here,
  the agent). It manages the conversation and decides when to use an
  external capability.
- **MCP client**: a connector inside the host. It talks to one MCP
  server. A host connected to two servers has two clients.
- **MCP server**: a separate program that exposes capabilities. Here,
  `learning_server.py` exposes the learning topics.
- **Tools**: actions the server runs when asked, with inputs and a
  result (for example `search_topics("decorators")`).
- **Resources**: read-only data the server makes available (for
  example the topic catalog).

**Example:** the agent needs information about "Python decorators".
Its MCP client asks the learning server, the server reads
`topics.json` and returns the topic, and the agent uses it in its
answer.

**Least privilege:** a server should expose only what it really
needs. Fewer capabilities means fewer ways to misuse it (a learning
server should read topics, not delete files) and a smaller server
that is easier to test.

## Requirements

- Python 3.10 or newer (tested with Python 3.12 on Ubuntu 24.04, WSL)
- `fastmcp` (listed in `requirements.txt`)
- No API key, no database, no internet access at runtime

## Setup

    git clone https://github.com/giosue2007/mcp-learning-project.git
    cd mcp-learning-project
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

`.env.example` documents optional variables for an LLM-based agent
(Ollama). The current agent does not use them; no `.env` is needed.

## How to Run the Server

    python3 server/learning_server.py

The server uses the **stdio** transport. After the FastMCP banner it
waits silently for a client: this is normal. Stop it with `Ctrl + C`.
You usually do not start it by hand: the client and the agent start
it automatically as a subprocess.

## How to Test the Server

    python3 client/mcp_client.py 2>/dev/null

`client/mcp_client.py` starts the server, then checks that:

1. the server starts and the client connects;
2. the tools are listed;
3. `search_topics` works;
4. `get_topic_details` works;
5. the `topics://catalog` resource can be read;
6. invalid inputs return understandable results.

`2>/dev/null` only hides the FastMCP banner (printed on stderr).

## How to Run the Agent

    python3 client/agent.py 2>/dev/null
    python3 client/agent.py "How do I learn JavaScript promises?" 2>/dev/null

Without an argument, the agent uses the question
"I want to study Python decorators. What should I review first?".

The agent is a deterministic **agent-like client** (no LLM). It:

1. extracts the useful keywords of the question;
2. calls `search_topics` through MCP for each keyword and keeps the
   topic found most often;
3. calls `get_topic_details` through MCP for that topic;
4. writes a short answer and saves it in
   `output/sample_agent_response.md`.

It never imports the server functions: everything goes through MCP.

## Available Tools

| Tool | Input | Output |
|------|-------|--------|
| `search_topics` | `query: str` | List of `{id, title, summary}` whose title or key concepts contain every word of the query. `[]` if nothing matches or the query is empty. |
| `get_topic_details` | `topic_id: str` | The full topic (summary, prerequisites, key concepts, common mistakes, practice idea). If the id does not exist: `{"error": ..., "available_ids": [...]}`. |

## Available Resources

| URI | Content |
|-----|---------|
| `topics://catalog` | Read-only JSON list of every topic `{id, title}`. |

## Third-Party MCP Server Review

**Server reviewed:** Filesystem MCP Server
(`@modelcontextprotocol/server-filesystem`), a reference server from
the official `modelcontextprotocol/servers` repository. I reviewed its
README and configuration examples; I did not install it.

**What it does:** lets an AI application read, write, search and
organize files inside directories chosen by the user.

**Local or remote:** local. The client starts it as a subprocess
(`npx` or `docker run -i`) and talks to it over stdio. No network
endpoint is exposed.

**Tools exposed:** `read_text_file`, `read_media_file`,
`read_multiple_files`, `write_file`, `edit_file`, `create_directory`,
`list_directory`, `list_directory_with_sizes`, `move_file`,
`search_files`, `directory_tree`, `get_file_info`,
`list_allowed_directories`.

**Permissions / credentials:** no API key or account. The only
permission is file-system access: the allowed directories are given
as command-line arguments (or as MCP roots by the client). Every
operation is restricted to those directories.

**Risk:** `write_file`, `edit_file` and `move_file` can overwrite or
move files without asking. With a broad folder (for example the home
directory), a wrong or manipulated request from the AI could damage
or read private files.

**Safety measure:** allow only one small project folder, never the
home directory. With Docker, mount it read-only (`ro`) when the AI
only needs to read. Use `edit_file` with `dryRun` to preview changes.

## Example Output

`python3 client/mcp_client.py 2>/dev/null` (shortened):

    1. Server started and connected.
    2. Tools: ['search_topics', 'get_topic_details']
    3. search_topics('decorators'): [{'id': 'python-decorators', ...}]
    6. Invalid inputs:
       search_topics('javascript'): []
       get_topic_details('unknown'): Topic 'unknown' not found.

`python3 client/agent.py 2>/dev/null` (shortened, full version in
`output/sample_agent_response.md`):

    ## Recommended topic
    Python Decorators
    ## Prerequisites
    - Functions
    - Scope
    ## Practice idea
    Create a decorator that logs function calls.

## Known Limitations

- **Small dataset:** only 5 topics. Any other subject (JavaScript,
  SQL...) returns "No matching topic was found".
- **Simple search:** plain substring matching on titles and key
  concepts. No synonyms or typo tolerance: "decorator" matches
  "decorators", but "decoratr" or "function wrappers" do not.
- **Keyword extraction:** the agent removes a fixed list of stop
  words. A question with unusual wording may pick a weaker topic.
- **No LLM:** the answer is a fixed template. It is reliable and never
  invents details, but it cannot rephrase or answer follow-up
  questions.
- **stdio only:** the server is started locally by the client; it is
  not exposed over HTTP.
- **Data reloaded on each call:** fine for 5 topics, but a larger
  dataset would need caching.

Problems met during development:

- Searching with the whole question returned nothing (every word must
  match), so the agent sends one keyword at a time.
- `output/*` was ignored by Git, so the sample response was not
  pushed; an exception was added to `.gitignore`.
- Long code blocks were cut when pasted into the terminal; files were
  written in smaller parts.

## Reflection

**1. What problem does MCP solve?**

An AI model only knows what it learned during training. MCP gives it
a standard way to reach external data and actions. Without MCP, each
application needs custom code for each source; with MCP, any
compatible client can use any compatible server.

**2. What is the difference between an MCP tool and an MCP resource?**

A tool is an action the client calls with inputs and that returns a
result (`search_topics(query)`). A resource is read-only data the
client reads by its URI (`topics://catalog`). Tools do something;
resources are just read.

**3. What does your MCP server expose?**

Two tools, `search_topics` and `get_topic_details`, and one resource,
`topics://catalog`. All of them only read `data/topics.json`; nothing
can modify the data.

**4. How does your agent use the MCP server?**

The agent starts the server through a FastMCP client (stdio). It calls
`search_topics` for each keyword of the question, picks the best
topic, calls `get_topic_details`, and builds the answer only from the
returned data. It never imports the server code.

**5. What should you check before using a third-party MCP server?**

Who publishes it and whether the source is official; whether it runs
locally or remotely; which tools and resources it exposes (especially
the ones that write, delete or send data); which credentials and
directories it needs; and whether access can be limited (read-only,
one folder, no personal credentials).

**6. What limitation did you observe in your implementation?**

The search is very literal: it only finds a topic when the exact
words appear in the title or key concepts, so the agent depends on
good keywords and on a very small dataset.
