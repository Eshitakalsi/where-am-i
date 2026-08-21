import re
from pathlib import Path

IGNORE_CMDS = {"ls", "cd", "pwd", "clear", "exit", "history", "echo", "cat", "man", "which"}

# Commands worth showing even without project context
ALWAYS_SHOW_PREFIXES = ("git ", "docker", "pip ", "npm ", "python ", "python3 ", "make ", "curl ", "brew ")


def _is_project_relevant(cmd: str, project_name: str, project_path: str) -> bool:
    cmd_lower = cmd.lower()
    return (
        project_name in cmd_lower
        or project_path in cmd_lower
        or any(cmd.startswith(p) for p in ALWAYS_SHOW_PREFIXES)
    )


def _dedupe(commands: list[str]) -> list[str]:
    seen = set()
    result = []
    for cmd in commands:
        if cmd not in seen:
            seen.add(cmd)
            result.append(cmd)
    return result


def _parse_zsh_history(path: Path, limit: int, project_name: str, project_path: str) -> list[str]:
    commands = []
    try:
        with open(path, "rb") as f:
            content = f.read().decode("utf-8", errors="replace")
        for line in reversed(content.splitlines()):
            line = line.strip()
            match = re.match(r"^: \d+:\d+;(.+)$", line)
            if match:
                cmd = match.group(1).strip()
            elif line.startswith(":"):
                continue
            else:
                cmd = line
            parts = cmd.split()
            if not cmd or len(cmd) <= 2 or (parts and parts[0] in IGNORE_CMDS):
                continue
            if _is_project_relevant(cmd, project_name, project_path):
                commands.append(cmd)
            if len(commands) >= limit:
                break
    except (PermissionError, FileNotFoundError):
        pass
    return _dedupe(list(reversed(commands)))


def _parse_bash_history(path: Path, limit: int, project_name: str, project_path: str) -> list[str]:
    commands = []
    try:
        with open(path, "r", errors="replace") as f:
            lines = f.readlines()
        for line in reversed(lines):
            cmd = line.strip()
            parts = cmd.split()
            if not cmd or len(cmd) <= 2 or cmd.startswith("#"):
                continue
            if parts and parts[0] in IGNORE_CMDS:
                continue
            if _is_project_relevant(cmd, project_name, project_path):
                commands.append(cmd)
            if len(commands) >= limit:
                break
    except (PermissionError, FileNotFoundError):
        pass
    return _dedupe(list(reversed(commands)))


def get_recent_commands(limit: int = 15, project_name: str = "", project_path: str = "") -> list[str]:
    home = Path.home()
    zsh_history = home / ".zsh_history"
    bash_history = home / ".bash_history"

    if zsh_history.exists():
        return _parse_zsh_history(zsh_history, limit, project_name, project_path)
    elif bash_history.exists():
        return _parse_bash_history(bash_history, limit, project_name, project_path)
    return []
