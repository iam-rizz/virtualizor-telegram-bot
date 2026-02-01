import asyncio
import subprocess
import httpx
import re
from pathlib import Path
from src.version import __version__
from src.logger import setup_logger

logger = setup_logger()

GITHUB_RAW_URL = "https://raw.githubusercontent.com/iam-rizz/virtualizor-telegram-bot/main/src/version.py"
CHECK_INTERVAL = 3600
UPDATE_SCRIPT = Path(__file__).parent.parent / "update.sh"

_cached_version = None
_last_check = 0


def parse_version(version_str: str) -> tuple:
    match = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", version_str)
    if match:
        major, minor, patch = match.groups()
        return (int(major), int(minor), int(patch) if patch else 0)
    return (0, 0, 0)


def is_newer_version(remote: str, local: str) -> bool:
    return parse_version(remote) > parse_version(local)


async def check_for_updates() -> dict:
    global _cached_version, _last_check

    import time

    current_time = time.time()

    if _cached_version and (current_time - _last_check) < CHECK_INTERVAL:
        return _cached_version

    result = {
        "current": __version__,
        "latest": __version__,
        "update_available": False,
        "error": None,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(GITHUB_RAW_URL)
            if response.status_code == 200:
                content = response.text
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    result["latest"] = match.group(1)
                    result["update_available"] = is_newer_version(
                        result["latest"], result["current"]
                    )
    except Exception as e:
        result["error"] = str(e)
        logger.debug(f"Update check failed: {e}")

    _cached_version = result
    _last_check = current_time
    return result


def run_update() -> dict:
    result = {"success": False, "message": ""}

    if not UPDATE_SCRIPT.exists():
        result["message"] = "update.sh not found"
        return result

    try:
        process = subprocess.Popen(
            ["bash", str(UPDATE_SCRIPT)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=UPDATE_SCRIPT.parent,
        )
        result["success"] = True
        result["message"] = "Update started. Bot will restart shortly."
    except Exception as e:
        result["message"] = str(e)

    return result
