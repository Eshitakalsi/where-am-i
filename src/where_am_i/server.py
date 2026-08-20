import os
from mcp.server.mcpserver.server import MCPServer

from .collectors.files import get_recent_files
from .collectors.git import get_git_state
from .collectors.processes import get_running_processes, get_docker_containers
from .collectors.shell import get_recent_commands
from .collectors.editor import get_vscode_open_files

server = MCPServer("where-am-i")


def _format_snapshot(base_dir: str) -> str:
    lines = [f"# Where Am I?\n", f"**Working directory:** `{base_dir}`\n"]

    # --- Git ---
    git_repos = get_git_state(base_dir)
    if git_repos:
        lines.append("## Git State")
        for repo in git_repos:
            rel = os.path.relpath(repo["repo"], base_dir) or "."
            lines.append(f"\n**Repo:** `{rel}` — branch `{repo['branch']}`")
            if repo["uncommitted_changes"]:
                lines.append("Uncommitted changes:")
                for change in repo["uncommitted_changes"]:
                    lines.append(f"  {change}")
            else:
                lines.append("Working tree clean.")
            if repo["recent_commits"]:
                lines.append("Recent commits:")
                for commit in repo["recent_commits"]:
                    lines.append(f"  {commit}")
            if repo["stashes"]:
                lines.append(f"Stashes: {repo['stashes']}")

    # --- Recently edited files ---
    recent_files = get_recent_files(base_dir, minutes=60)
    if recent_files:
        lines.append("\n## Recently Edited Files (last 60 min)")
        for f in recent_files:
            lines.append(f"  {f['modified_ago_mins']}m ago — `{f['path']}`")

    # --- VS Code ---
    vscode_files = get_vscode_open_files()
    if vscode_files:
        lines.append("\n## VS Code")
        for f in vscode_files:
            lines.append(f"  {f}")

    # --- Shell history ---
    cmds = get_recent_commands(limit=15)
    if cmds:
        lines.append("\n## Recent Terminal Commands")
        for cmd in cmds:
            lines.append(f"  $ {cmd}")

    # --- Processes ---
    procs = get_running_processes()
    if procs:
        lines.append("\n## Running Dev Processes")
        for p in procs:
            lines.append(f"  [{p['pid']}] {p['name']} — {p['memory_mb']}MB")
            lines.append(f"       {p['cmd']}")

    # --- Docker ---
    containers = get_docker_containers()
    if containers:
        lines.append("\n## Docker Containers")
        for c in containers:
            ports = f" ({c['ports']})" if c["ports"] else ""
            lines.append(f"  {c['name']} — {c['image']} — {c['status']}{ports}")

    if len(lines) == 2:
        lines.append("\nNothing detected in the current directory.")

    return "\n".join(lines)


@server.tool(
    description=(
        "Reconstructs your current dev session context. "
        "Shows recently edited files, git state, running processes, "
        "Docker containers, recent terminal commands, and VS Code open files. "
        "Call this when the user wants to know where they left off or what they were working on."
    )
)
def where_am_i(directory: str = "") -> str:
    """
    directory: Root directory to inspect. Defaults to current working directory.
    """
    base_dir = os.path.expanduser(directory) if directory else os.getcwd()
    return _format_snapshot(base_dir)


def main() -> None:
    server.run()


if __name__ == "__main__":
    main()
