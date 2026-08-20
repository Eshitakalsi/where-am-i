# where-am-i

An MCP server that reconstructs your dev session context on demand.

Ask Claude *"where am I?"* and it snapshots your current working state — git branches, recently edited files, running processes, Docker containers, terminal history, and VS Code workspaces — all in one response.

---

## What it shows

| Signal | What you get |
|---|---|
| **Git** | Branch, uncommitted changes, last 5 commits, stash count |
| **Files** | Files edited in the last 60 minutes |
| **VS Code** | Open workspaces |
| **Terminal** | Last 15 meaningful shell commands |
| **Processes** | Running dev processes (node, python, postgres, redis…) |
| **Docker** | Running containers with status and ports |

---

## Setup

**1. Clone and install**

```bash
git clone https://github.com/Eshitakalsi/where-am-i.git
cd where-am-i
pip install -e .
```

**2. Find your Python path**

```bash
which python
# e.g. /Users/yourname/.pyenv/versions/3.12.13/bin/python
```

**3. Add to Claude Desktop**

Open `~/Library/Application Support/Claude/claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "where-am-i": {
      "command": "/absolute/path/to/python",
      "args": ["-m", "where_am_i.server"]
    }
  }
}
```

**4. Restart Claude Desktop**

The tool is now available. Ask Claude:

> *"where am I?"*
> *"what was I working on?"*
> *"give me a snapshot of my dev session"*

To inspect a specific project directory, mention the path:

> *"where am I in ~/Desktop/projects/my-app"*

---

## Requirements

- Python 3.10+
- Claude Desktop
- `docker` CLI in PATH (optional — for container info)
- zsh or bash shell history
