import os
import time
from pathlib import Path

IGNORE_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".tox", "dist", "build", ".next"}
IGNORE_EXTENSIONS = {".pyc", ".pyo", ".log", ".lock", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".ttf"}


def get_recent_files(base_dir: str, minutes: int = 30, max_files: int = 20) -> list[dict]:
    base = Path(base_dir).expanduser().resolve()
    cutoff = time.time() - (minutes * 60)
    results = []

    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for fname in files:
            if Path(fname).suffix in IGNORE_EXTENSIONS:
                continue
            fpath = Path(root) / fname
            try:
                mtime = fpath.stat().st_mtime
                if mtime >= cutoff:
                    results.append({
                        "path": str(fpath.relative_to(base)),
                        "modified_ago_mins": round((time.time() - mtime) / 60, 1),
                    })
            except (PermissionError, FileNotFoundError):
                continue

    results.sort(key=lambda x: x["modified_ago_mins"])
    return results[:max_files]
