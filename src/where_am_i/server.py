import os
from pathlib import Path
from mcp.server.mcpserver.server import MCPServer

from .collectors.files import get_recent_files
from .collectors.git import get_git_state
from .collectors.processes import get_running_processes, get_docker_containers
from .collectors.shell import get_recent_commands
from .collectors.editor import get_vscode_open_files

server = MCPServer("where-am-i")


def _format_snapshot(base_dir: str) -> str:
    project_name = Path(base_dir).name
    sections = []

    # --- Git ---
    git_repos = get_git_state(base_dir)
    for repo in git_repos:
        rel = os.path.relpath(repo["repo"], base_dir) or "."
        block = [f"### GIT  `{rel}`"]
        block.append(f"Branch: **{repo['branch']}**")
        if repo["uncommitted_changes"]:
            block.append(f"Uncommitted ({len(repo['uncommitted_changes'])} files):")
            for c in repo["uncommitted_changes"]:
                block.append(f"  `{c}`")
        else:
            block.append("Working tree: clean")
        if repo["stashes"]:
            block.append(f"Stashes: {repo['stashes']}")
        if repo["recent_commits"]:
            block.append("Last commits:")
            for c in repo["recent_commits"]:
                block.append(f"  `{c}`")
        sections.append("\n".join(block))

    # --- Recently edited files ---
    recent_files = get_recent_files(base_dir, minutes=60)
    if recent_files:
        block = ["### EDITED  `last 60 min`"]
        for f in recent_files:
            block.append(f"  {f['modified_ago_mins']}m  `{f['path']}`")
        sections.append("\n".join(block))

    # --- Shell history ---
    cmds = get_recent_commands(limit=20, project_name=project_name, project_path=base_dir)
    if cmds:
        block = ["### TERMINAL"]
        for cmd in cmds:
            block.append(f"  `$ {cmd}`")
        sections.append("\n".join(block))

    # --- VS Code ---
    vscode_files = [f for f in get_vscode_open_files() if not f.startswith("[workspace]")]
    if vscode_files:
        block = ["### VS CODE  open files"]
        for f in vscode_files:
            block.append(f"  `{f}`")
        sections.append("\n".join(block))

    # --- Processes ---
    procs = get_running_processes()
    if procs:
        block = ["### PROCESSES"]
        for p in procs:
            block.append(f"  `{p['name']}` pid {p['pid']} — {p['memory_mb']}MB")
        sections.append("\n".join(block))

    # --- Docker ---
    containers = get_docker_containers()
    if containers:
        block = ["### DOCKER"]
        for c in containers:
            ports = f"  {c['ports']}" if c["ports"] else ""
            block.append(f"  `{c['name']}` {c['image']} — {c['status']}{ports}")
        sections.append("\n".join(block))

    header = f"## where-am-i  `{project_name}`\n> {base_dir}"
    return header + "\n\n---\n\n" + "\n\n---\n\n".join(sections) if sections else header + "\n\nNothing detected."


@server.tool(
    description=(
        "Reconstructs the developer's current session context for a given project directory. "
        "Returns a structured snapshot covering: git state, recently edited files, "
        "recent terminal commands, running dev processes, and Docker containers. "
        "Call this when the user asks where they left off, what they were working on, or wants a session snapshot. "
        "When presenting results: render git state, edited files, processes, and docker sections verbatim. "
        "For the TERMINAL section, do not dump the commands — instead write 1-2 sentences explaining "
        "what the developer was doing based on the sequence of commands (e.g. 'you were setting up remote tracking, then switched to a fixes branch')."
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
