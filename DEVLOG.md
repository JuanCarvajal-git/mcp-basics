# Devlog

Running record of what we've built, in order. Newest entries at the bottom.

---

## Entry 1 — 2026-09-17 — The simplest possible server

**Goal:** get one working MCP server running, nothing else.

**Files:**
- `server.py` — the whole server, 10 lines.
- `requirements.txt` — one dependency: `mcp[cli]`.

**What it does:**
Exposes exactly one tool, `hello(name)`, which returns a greeting string. That's it — no web fetching, no local program calls, no report writing yet. Those come later, one at a time.

**How it works, piece by piece:**
- `FastMCP("my-first-server")` creates the server object. The string is just a display name.
- `@mcp.tool()` is a decorator — it takes a normal Python function and registers it as something the AI client can call. It reads the function's type hints (`name: str`) to build the input schema automatically, and uses the docstring (`"""Greet someone by name."""`) as the description the AI sees when deciding whether to call this tool.
- `mcp.run()` starts the server listening over stdio (standard input/output) — the simplest transport, meant to be launched as a subprocess by whatever client you point at it (Claude Desktop, Claude Code, etc).

**How to run it:**
```bash
cd mcp-project
pip install -r requirements.txt
python server.py
```
It'll just sit there waiting — it's meant to be launched by a client, not used standalone from the terminal. Next step is wiring it into a client so you can actually call `hello` and see it respond.

**Status:** done, untested by a real client yet.

---

## Entry 2 — 2026-09-17 — Dependency management: use uv

**Decision:** use a virtual environment for this project, via `uv` rather than plain `venv`/`pip`.

**Why a virtual environment at all:** without one, dependencies install into the system-wide Python, causing version conflicts across projects and making the setup non-reproducible elsewhere.

**Why `uv` specifically:**
- Single fast tool (Rust-based) that replaces both `venv` and `pip`.
- It's what the official MCP quickstart docs use, so it matches what most tutorials/examples assume.
- Alternatives considered: `venv`+`pip` (built-in, but slower and two tools instead of one), `poetry`/`pipenv` (heavier tooling, unnecessary complexity for this stage).

**Setup commands:**
```bash
cd mcp-project
uv venv
source .venv/bin/activate     # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```
Or, using uv's project mode to skip manual venv creation:
```bash
uv add mcp[cli]
```

**Status:** decision made, not yet reflected in project files (no `pyproject.toml` yet — still using plain `requirements.txt` from Entry 1).

---

## Entry 3 — 2026-09-17 — Client: GitHub Copilot (Agent mode) in VS Code, via WSL

**Setup confirmed:** using VS Code connected to a WSL folder, with GitHub Copilot Free as the AI client (not Claude Desktop or Claude Code CLI).

**Key fact:** MCP support and Agent mode are available to all VS Code users, including Copilot's free tier — this is a VS Code feature, not gated behind a paid Copilot plan. The free tier limits monthly request count, not tool/protocol access.

**How to connect the server:**
1. Copilot Chat panel → switch mode dropdown to **Agent** (MCP tools are only called in Agent mode).
2. Create `.vscode/mcp.json` in the project root (inside the WSL filesystem, since VS Code is connected to WSL):
   ```json
   {
     "servers": {
       "my-first-server": {
         "type": "stdio",
         "command": "uv",
         "args": ["run", "--directory", "/path/to/mcp-project", "python", "server.py"]
       }
     }
   }
   ```
3. Start the server via the "Start" code-lens above the entry in `mcp.json`, or **MCP: List Servers** in the command palette.
4. Prompt the agent normally, e.g. "call the hello tool with name 'Alex'" — no special syntax needed, Copilot sees the tool is available and calls it.

**Status:** instructions given, not yet confirmed working on the user's machine.

---

## Entry 4 — 2026-09-17 — Migrating to a real uv project, and running the server

**Change:** converted the plain `requirements.txt` setup into an actual `uv` project.

```bash
cd mcp-project
uv add "mcp[cli]"
```
This creates `pyproject.toml` + `.venv/` + `uv.lock` in one step, replacing the manual `pip install -r requirements.txt` flow from Entry 1. (`requirements.txt` is now superseded — `pyproject.toml`/`uv.lock` are the source of truth going forward.)

**How to run the server manually (sanity check only):**
```bash
uv run python server.py
```
`uv run` finds and uses the project's `.venv` automatically.

**Important behavior note:** running it prints nothing and the terminal just hangs — this is correct. A stdio MCP server waits silently for a client to talk to it over stdin/stdout; it doesn't print or exit on its own. `Ctrl+C` to stop it. A Python traceback instead of a silent hang is the actual failure signal to watch for.

**Normal usage vs. manual run:** day-to-day, don't run it manually — use the "Start" code-lens in `.vscode/mcp.json` (Entry 3) so Copilot manages the process lifecycle. Manual `uv run` is just for debugging/verifying it starts clean.

**Status:** instructions given, awaiting confirmation it runs without errors on the user's machine.

---

## Entry 5 — 2026-09-17 — Fixing uv's package-build error

**Problem 1:** `uv init --no-readme` scaffolded a `src/mcp_project/__init__.py` layout (library-style project), not a plain script layout.

**Problem 2 (resulting error):** `uv run python server.py` failed with:
```
Failed to build `mcp-project @ file:///.../mcp-project`
cause: Expected a Python module at: src/mcp_project/__init__.py
```
This happened because `uv` was trying to install the project itself as a package (library), which requires a proper `src/<pkg>/__init__.py` structure — we don't have or need that, since `server.py` is just a script, not a library to publish.

**Fix:** tell uv this project isn't a package to build, via `pyproject.toml`:
```toml
[tool.uv]
package = false
```
Then remove the now-unneeded scaffold:
```bash
rm -rf src
```
`server.py` stays at the project root — it does not move into `src/`.

**Status:** fix given, awaiting confirmation `uv run python server.py` now runs clean (silent hang = success).

---

## Entry 6 — 2026-09-17 — Full reset: clean working setup, start to finish

Previous entries (1–5) documented the trial-and-error. This entry is the consolidated, known-good sequence — use this as the reference going forward, not the earlier ones.

**1. Fresh folder:**
```bash
mkdir mcp-project && cd mcp-project
```

**2. Init uv project as a plain script (not a library):**
```bash
uv init --no-readme
rm -rf src
```

**3. Disable package-build mode** (this was the root cause of Entry 5's error):
```bash
cat >> pyproject.toml << 'EOF'

[tool.uv]
package = false
EOF
```

**4. Add dependency:**
```bash
uv add "mcp[cli]"
```

**5. Server code** (`server.py`) — one tool, `hello`:
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-first-server")

@mcp.tool()
async def hello(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

**6. Sanity check:**
```bash
uv run python server.py
```
Expected: silent hang (no output, no traceback). `Ctrl+C` to stop. This is correct — a stdio server waits for a client, it doesn't print anything on its own.

**7. Client config** (`.vscode/mcp.json`), path filled in via `pwd`:
```json
{
  "servers": {
    "my-first-server": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/mcp-project", "python", "server.py"]
    }
  }
}
```

**8. Using it in Copilot:**
- Command Palette → **MCP: List Servers** → `my-first-server` → Start.
- Copilot Chat mode dropdown → **Agent**.
- Prompt: `call the hello tool with name "Alex"`.

**Status:** awaiting confirmation of step 6 (server runs clean) before proceeding to step 7/8.

---

## Entry 7 — 2026-09-17 — mcp SDK v2: FastMCP renamed to MCPServer

**Error hit:**
```
ModuleNotFoundError: No module named 'mcp.server.fastmcp'.
This is mcp 2.x, where FastMCP was renamed to MCPServer...
```

**Cause:** `uv add "mcp[cli]"` (Entry 6) installed an unpinned dependency, which resolved to the newest release — and the `mcp` Python SDK had a major v2 release that renamed the `FastMCP` class to `MCPServer` and moved its import path. Nothing wrong with our setup; the original code was written against the old v1 API name.

**Fix — updated `server.py`:**
```python
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("my-first-server")

@mcp.tool()
async def hello(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run()
```

Only the import and class name changed (`FastMCP` → `MCPServer`, `mcp.server.fastmcp` → `mcp.server.mcpserver`). The `@mcp.tool()` decorator, function signature, and `mcp.run()` are identical to v1 — no other code needs to change for a server this simple.

**Status:** fix applied, awaiting confirmation `uv run python server.py` runs clean.

---

## Entry 8 — 2026-09-17 — Visual testing with MCP Inspector

**Tool:** MCP Inspector — official web UI for manually testing an MCP server (lists tools, lets you call them via a form) without needing a full client like Copilot.

**Command:**
```bash
uv run npx @modelcontextprotocol/inspector python server.py
```
(Note: package name is `@modelcontextprotocol/inspector` — a typo'd `@modelcontextprotocl/inspector` gives a 404 from npm.)

**Usage:** opens a local URL (e.g. `http://localhost:6274`) in the browser; `hello` should appear as a listed tool, callable via a form with a `name` field.

**Status:** command corrected, awaiting confirmation it opens and lists `hello` correctly.

---

## Entry 9 — 2026-09-17 — Inspector: npm native-binding error

**Error hit:**
```
Error running MCP Inspector: Cannot find native binding. npm has a bug related to
optional dependencies (https://github.com/npm/cli/issues/4828)...
```

**Likely cause:** known npm bug with optional native dependencies not resolving correctly, especially common in WSL when npm's cache/PATH gets confused about which OS/architecture binaries to fetch — sometimes because a Windows `npm`/`node` is being picked up instead of a WSL-native one.

**Fix attempted, in order:**
```bash
npm cache clean --force
rm -rf ~/.npm/_npx
which npm    # should print /usr/... or /home/... — NOT /mnt/c/...
which node   # same check
uv run npx @modelcontextprotocol/inspector python server.py
```

**Status:** diagnostic steps given, awaiting output of `which npm` / `which node` to confirm whether this is the npm cache bug or a Windows-Node-leaking-into-WSL issue.

---

## Entry 10 — 2026-09-17 — Extending the server: driving Fiji (ImageJ) on .tif images

**Goal:** give the agent general-purpose access to Fiji's functions/plugins, applied to the user's own .tif images, from a WSL-based server calling a Windows .exe.

**Key design decision:** rather than hardcoding one operation (e.g. "blur"), expose Fiji's own **macro language** as a passthrough. One tool, `run_fiji_macro(macro_code)`, lets the agent generate arbitrary ImageJ macro code — this reaches any built-in function or installed plugin without us needing to write a wrapper per operation. This mirrors the "general purpose tool calling" idea from Entry 0 (the local-program tool from the original diagram).

**Key technical wrinkle:** Fiji is a Windows binary; the server runs in WSL. WSL can launch a Windows `.exe` directly, but paths must be Windows-style (`C:\...`) when handed to it — WSL-style paths (`/mnt/c/...`) aren't understood by the Windows program. Added a `to_windows_path()` helper using the `wslpath -w` command-line tool (ships with WSL by default) to convert automatically.

**New tools added to `server.py`:**
- `list_tif_images()` — lists `.tif`/`.tiff` files in the configured images folder, returned as full Windows-style paths (directly pasteable into macro code).
- `run_fiji_macro(macro_code, timeout_seconds=180)` — writes the given ImageJ macro code to a temp `.ijm` file inside the images folder, converts its path to Windows format, runs Fiji headlessly (`--headless --console -macro <path>`), captures and returns console output, then cleans up the temp file.

**Configuration required (user-specific, left as placeholders):**
```python
FIJI_EXE_PATH = "/mnt/c/PATH/TO/fiji-windows-x64.exe"
IMAGES_DIR = "/mnt/c/PATH/TO/your/tif/images"
```

**Status:** code written, awaiting user to fill in real paths and confirm it runs.

---

## Entry 11 — 2026-09-17 — Back to basics: a small toolset for a "MCP basics" repo

**Context shift:** paused the Fiji/image-processing extension (Entry 10) to instead finalize a clean, simple reference server intended for a public GitHub repo.

**`server.py` rewritten with five simple tools**, chosen to each illustrate a different pattern while staying trivial to read:
- `hello(name)` — string in, string out (the original starter tool).
- `add(a, b)` — basic numeric input/output.
- `reverse_text(text)` — simple string manipulation.
- `word_count(text)` — text processing returning a formatted string.
- `is_prime(n)` — a tool with actual logic/branching, not just a one-liner.

**Also added, for the GitHub repo:**
- `README.md` — setup, run, test (Inspector), and Copilot/VS Code connection instructions, condensed from earlier devlog entries.
- `.gitignore` — excludes `.venv/`, `__pycache__/`, `*.pyc`, `.env`.

**Repo structure at this point:**
```
mcp-project/
├── server.py
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
├── DEVLOG.md
└── .vscode/mcp.json   (from Entry 3/6)
```

**Status:** ready to push to GitHub once confirmed working via Inspector and/or Copilot.
