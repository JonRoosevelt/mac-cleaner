"""Execute allowlisted official cleanup commands."""

from __future__ import annotations

import logging
import shutil
import subprocess

from mac_cleaner.safety import SAFE_PATHS, validate_target
from mac_cleaner.utils import free_bytes

COMMANDS = {
    "npm": ("npm", "cache", "clean", "--force"),
    "pip": ("python3", "-m", "pip", "cache", "purge"),
    "yarn": ("yarn", "cache", "clean"),
    "jest": ("jest", "--clearCache"),
    "uv": ("uv", "cache", "prune"),
    "go": ("go", "clean", "-cache"),
}


def cleanup(category: str, logger: logging.Logger) -> tuple[bool, str]:
    target = SAFE_PATHS.get(category)
    if target is None or not validate_target(target, category):
        return False, "Target rejected by safety policy"
    before = free_bytes()
    if category == "gh":
        if not target.exists() or target.is_symlink():
            return True, "GitHub CLI cache not present"
        removed = 0
        for candidate in target.iterdir():
            if (
                candidate.name.startswith("run-log-")
                and candidate.name.endswith(".zip")
                and candidate.is_file()
                and not candidate.is_symlink()
                and validate_target(candidate.parent, category)
            ):
                candidate.unlink()
                removed += 1
        logger.info("category=%s removed_run_log_archives=%d", category, removed)
        return True, f"Removed {removed} run-log archive(s); reclaimed estimate follows"
    command = COMMANDS[category]
    executable = shutil.which(command[0])
    if executable is None:
        return False, f"Required tool not found: {command[0]}"
    try:
        result = subprocess.run(
            (executable, *command[1:]), check=False, capture_output=True, text=True
        )
    except OSError as exc:
        return False, f"Could not run {command[0]}: {exc}"
    if result.returncode:
        detail = result.stderr.strip() or f"exit code {result.returncode}"
        logger.error("category=%s failed=%s", category, detail)
        return False, f"{command[0]} failed: {detail}"
    logger.info("category=%s command=%s free_before=%d", category, " ".join(command), before)
    return True, result.stdout.strip() or f"Completed {command[0]} cleanup"
