import subprocess
import psutil

DEV_PROCESS_NAMES = {
    "node", "python", "python3", "ruby", "go", "java", "gradle", "mvn",
    "uvicorn", "gunicorn", "webpack", "vite",
    "postgres", "mysqld", "redis-server", "mongod",
    "nginx", "caddy", "docker",
}

IGNORE_PROCESS_NAMES = {
    "google chrome", "google chrome helper", "safari", "firefox",
    "code helper", "electron", "slack", "zoom", "spotify",
}


def get_running_processes() -> list[dict]:
    found = []
    for proc in psutil.process_iter(["pid", "name", "cmdline", "cpu_percent", "memory_info"]):
        try:
            name = (proc.info["name"] or "").lower()
            if any(ig in name for ig in IGNORE_PROCESS_NAMES):
                continue
            if name in DEV_PROCESS_NAMES:
                found.append({
                    "pid": proc.info["pid"],
                    "name": proc.info["name"],
                    "cmd": " ".join(proc.info["cmdline"] or [])[:120],
                    "memory_mb": round(proc.info["memory_info"].rss / 1024 / 1024, 1) if proc.info["memory_info"] else 0,
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return found[:15]


def get_docker_containers() -> list[dict]:
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True, text=True, timeout=5
        )
        containers = []
        for line in result.stdout.strip().splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                containers.append({
                    "name": parts[0],
                    "image": parts[1],
                    "status": parts[2],
                    "ports": parts[3] if len(parts) > 3 else "",
                })
        return containers
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []
