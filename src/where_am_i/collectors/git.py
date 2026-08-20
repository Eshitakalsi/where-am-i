import subprocess
from pathlib import Path


def _run(cmd: list[str], cwd: str) -> str:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def _find_git_repos(base_dir: str, max_depth: int = 3) -> list[str]:
    base = Path(base_dir).expanduser().resolve()
    seen = set()
    repos = []
    for item in base.rglob(".git"):
        depth = len(item.relative_to(base).parts)
        if depth <= max_depth and item.is_dir():
            repo_path = str(item.parent)
            if repo_path not in seen:
                seen.add(repo_path)
                repos.append(repo_path)
    return repos[:5]


def get_git_state(base_dir: str) -> list[dict]:
    repos = _find_git_repos(base_dir)
    results = []

    for repo in repos:
        branch = _run(["git", "branch", "--show-current"], repo)
        status = _run(["git", "status", "--short"], repo)
        recent_commits = _run(["git", "log", "--oneline", "-5"], repo)
        stash_count = len(_run(["git", "stash", "list"], repo).splitlines())

        results.append({
            "repo": repo,
            "branch": branch or "unknown",
            "uncommitted_changes": [line for line in status.splitlines() if line.strip()],
            "recent_commits": [line for line in recent_commits.splitlines() if line.strip()],
            "stashes": stash_count,
        })

    return results
