"""Discover known cache sizes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mac_cleaner.safety import REVIEW_PATHS, SAFE_PATHS, safe_size


@dataclass(frozen=True)
class Candidate:
    name: str
    category: str
    path: Path
    size: int
    cleaner: str | None = None


CLEANER_NAMES = {
    "npm": "npm cache clean --force",
    "pip": "python -m pip cache purge",
    "yarn": "yarn cache clean",
    "jest": "jest --clearCache",
    "gh": "remove run-log-*.zip only",
    "uv": "uv cache prune",
    "go": "go clean -cache",
}


def scan() -> list[Candidate]:
    items = [
        Candidate(name, "SAFE", path, safe_size(path), CLEANER_NAMES[name])
        for name, path in SAFE_PATHS.items()
    ]
    items.extend(
        Candidate(name, "REVIEW", path, safe_size(path)) for name, path in REVIEW_PATHS.items()
    )
    return items
