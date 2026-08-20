import os
import re
from pathlib import Path

IGNORE_CMDS = {"ls", "cd", "pwd", "clear", "exit", "history", "echo", "cat", "man", "which"}


def _parse_zsh_history(path: Path, limit: int) -> list[str]:
    commands = []
    try:
        with open(path, "rb") as f:
            content = f.read().decode("utf-8", errors="replace")
        # zsh extended history format: `: timestamp:elapsed;command`
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
            if cmd and len(cmd) > 2 and not any(parts[0] == ig for ig in IGNORE_CMDS if parts):
                commands.append(cmd)
            if len(commands) >= limit:
                break
    except (PermissionError, FileNotFoundError):
        pass
    return list(reversed(commands))


def _parse_bash_history(path: Path, limit: int) -> list[str]:
    commands = []
    try:
        with open(path, "r", errors="replace") as f:
            lines = f.readlines()
        for line in reversed(lines):
            cmd = line.strip()
            parts = cmd.split()
            if cmd and len(cmd) > 2 and not cmd.startswith("#"):
                if not any(parts[0] == ig for ig in IGNORE_CMDS if parts):
                    commands.append(cmd)
            if len(commands) >= limit:
                break
    except (PermissionError, FileNotFoundError):
        pass
    return list(reversed(commands))


def get_recent_commands(limit: int = 20) -> list[str]:
    home = Path.home()
    zsh_history = home / ".zsh_history"
    bash_history = home / ".bash_history"

    if zsh_history.exists():
        return _parse_zsh_history(zsh_history, limit)
    elif bash_history.exists():
        return _parse_bash_history(bash_history, limit)
    return []
