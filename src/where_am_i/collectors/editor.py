import json
import sqlite3
from pathlib import Path


def _get_vscode_storage_path() -> Path | None:
    candidates = [
        Path.home() / "Library/Application Support/Code/User/workspaceStorage",
        Path.home() / ".config/Code/User/workspaceStorage",
        Path.home() / "AppData/Roaming/Code/User/workspaceStorage",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def get_vscode_open_files() -> list[str]:
    storage = _get_vscode_storage_path()
    if not storage:
        return []

    open_files = []
    # Each workspace has a folder with a storage.json or backup files
    for workspace_dir in sorted(storage.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
        backup_dir = workspace_dir / "backup"
        if backup_dir.exists():
            for ftype in ("untitled", "file"):
                ftype_dir = backup_dir / ftype
                if ftype_dir.exists():
                    for f in ftype_dir.iterdir():
                        if f.is_file() and f.suffix != ".json":
                            open_files.append(str(f.name))

        # Also try reading workspace.json for the folder path
        ws_json = workspace_dir / "workspace.json"
        if ws_json.exists():
            try:
                data = json.loads(ws_json.read_text())
                folder = data.get("folder", "")
                if folder:
                    open_files.insert(0, f"[workspace] {folder}")
            except (json.JSONDecodeError, PermissionError):
                pass

    return open_files[:20]
