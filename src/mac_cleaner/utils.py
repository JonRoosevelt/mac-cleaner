"""Shared formatting, disk, and logging utilities."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path


def format_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} TB"


def free_bytes(path: Path | None = None) -> int:
    return shutil.disk_usage(path or Path.home()).free


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("mac_cleaner")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    log_dir = Path.home() / "Library" / "Logs" / "mac-cleaner"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_dir / "cleanup.log")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    except OSError:
        logger.addHandler(logging.NullHandler())
    return logger
