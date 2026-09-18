# mcp-basics

Basic MCP server that can access simple tools.

## Setup and local server startup

This section explains how to set up the project and run the server locally before using it with an MCP client or the inspector.

### 1. Open the project folder

```bash
cd /home/jmcar/projects/mcp-hackaton/mcp-basics
```

### 2. Install dependencies with uv

```bash
uv sync
```

This creates and updates the local environment in `.venv/` and installs the packages declared in `pyproject.toml`.

### 3. Start the MCP server

```bash
uv run python server.py
```

This launches the server in stdio mode. The process stays alive and waits for MCP requests from a client.

### 4. If you want to visualize it in the MCP Inspector

Sometimes the inspector or npm cache can have stale state. Use these commands:

```bash
npm cache clean --force
rm -rf ~/.npm/_npx
uv run npx @modelcontextprotocol/inspector python server.py
```

These steps help clear cached npm data and then launch the MCP Inspector against the local Python server so you can inspect the tools, requests, and responses visually.

## Quick Start

### 1. Start the server

From the project folder:

```bash
uv run python server.py
```

This starts the MCP server and keeps it running in stdio mode, waiting for a client to send requests.

### 2. Call a tool

The server exposes several tools. The original one is `hello`, and the project also includes arithmetic, text manipulation, word counting, and primality checks.

Example calls:

```python
await session.call_tool("hello", {"name": "Juan"})
await session.call_tool("add", {"a": 4, "b": 6})
await session.call_tool("reverse_text", {"text": "python"})
await session.call_tool("word_count", {"text": "three words here"})
await session.call_tool("is_prime", {"n": 13})
```

Expected results:

```python
"Hello, Juan!"
"10"
"nohtyp"
"4 words"
"13 is prime."
```

### 3. Client config

The server is configured in [.vscode/mcp.json](.vscode/mcp.json):

```json
{
  "servers": {
    "my-first-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/home/jmcar/projects/mcp-hackaton/mcp-basics", "python", "server.py"]
    }
  }
}
```

That tells the MCP client how to launch the server automatically.

## Project structure and purpose

This folder contains the minimal files needed to run a small MCP server. Each item has a specific role in the setup.

### `server.py`

This is the main server implementation.

```python
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("my-first-server")

@mcp.tool()
async def hello(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

@mcp.tool()
async def add(a: float, b: float) -> str:
    """Add two numbers together."""
    return str(a + b)

@mcp.tool()
async def reverse_text(text: str) -> str:
    """Reverse a string."""
    return text[::-1]

@mcp.tool()
async def word_count(text: str) -> str:
    """Count the number of words in a piece of text."""
    count = len(text.split())
    return f"{count} word{'s' if count != 1 else ''}"

@mcp.tool()
async def is_prime(n: int) -> str:
    """Check whether a number is prime."""
    if n < 2:
        return f"{n} is not prime."
    for divisor in range(2, int(n ** 0.5) + 1):
        if n % divisor == 0:
            return f"{n} is not prime (divisible by {divisor})."
    return f"{n} is prime."

if __name__ == "__main__":
    mcp.run()
```

What it does:

- imports `MCPServer` from the `mcp` library
- creates a server instance named `my-first-server`
- registers multiple tools, each with a clear purpose
- accepts well-defined arguments for each tool
- returns string results that are easy for the client to read and display
- starts the MCP server when the file is executed directly

The server now exposes five tools:

- `hello(name)` — greeting helper
- `add(a, b)` — adds two numbers
- `reverse_text(text)` — reverses a string
- `word_count(text)` — counts the words in a sentence
- `is_prime(n)` — checks whether a number is prime

This is the core of the project: a single MCP server hosting multiple tools that a client can call.

### `pyproject.toml`

This file defines the Python project and its dependencies.

```toml
[project]
name = "mcp-basics"
version = "0.1.0"
requires-python = ">=3.14"
dependencies = [
    "mcp[cli]>=2.2.0",
]
```

Its purpose is to tell `uv` which Python version and libraries the project needs. In this case, it depends on the `mcp` package, which provides the server and client protocol support.

### `.vscode/mcp.json`

This file tells the client how to launch the server.

```json
{
  "servers": {
    "my-first-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/home/jmcar/projects/mcp-hackaton/mcp-basics", "python", "server.py"]
    }
  }
}
```

This matters because MCP servers are often started by a client, not by a normal terminal command alone. The config tells the client to run the server in the project directory and connect to it over standard input/output (`stdio`).

### `.venv/`

This is the local Python environment managed by `uv`. It contains the installed dependencies, including the `mcp` package.

The purpose of this folder is to isolate project dependencies from the system Python so the project runs consistently and without conflicts.

### `uv.lock`

This file locks the dependency versions used by the project.

It helps keep the environment reproducible so everyone working on the project uses the same installed versions of dependencies.

### `.python-version`

This file pins the Python version for the project.

It tells tools like `uv` which interpreter to use, helping avoid mismatches between the project and the local environment.

### `.gitignore`

This file tells Git which files should not be tracked, usually generated or local environment files such as `.venv/`.

It keeps the repository clean and avoids committing environment-specific data.

### `.git/`

This is the Git repository metadata folder. It stores the repository history, config, and other version-control information.

It is not part of the application itself; it is just for source control.

## How the files work together

The flow is straightforward:

1. `pyproject.toml` declares the project and dependencies.
2. `uv` creates the environment in `.venv/` and installs `mcp`.
3. `server.py` defines the server and registers all available tools.
4. `.vscode/mcp.json` tells the client how to launch that server.
5. When the client connects, the server starts with `mcp.run()`.
6. The client calls whichever tool it needs, such as `hello`, `add`, `reverse_text`, `word_count`, or `is_prime`.
7. The corresponding Python function runs and returns a string result.
8. The client receives that result through the MCP transport and can display it to the user or use it in a larger workflow.

In other words, this project is a small example of how a server can expose multiple callable utilities to an AI client while keeping each action simple and isolated.
