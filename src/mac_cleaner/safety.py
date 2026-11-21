"""Validated target policies. Never derive deletion targets from user input."""

from __future__ import annotations

from pathlib import Path

HOME = Path.home().resolve()

# Specific cache roots only; these are fixed policy targets, not arbitrary paths.
SAFE_PATHS = {
    "npm": HOME / ".npm",
    "pip": HOME / "Library" / "Caches" / "pip",
    "yarn": HOME / "Library" / "Caches" / "Yarn" / "v6",
    "jest": HOME / "Library" / "Caches" / "jest",
    "gh": HOME / "Library" / "Caches" / "gh",
    "uv": HOME / "Library" / "Caches" / "uv",
    "go": HOME / "Library" / "Caches" / "go-build",
}
REVIEW_PATHS = {
    "Playwright": HOME / "Library" / "Caches" / "ms-playwright",
    "Homebrew": HOME / "Library" / "Caches" / "Homebrew",
    "TypeScript": HOME / "Library" / "Caches" / "typescript",
    "HuggingFace": HOME / ".cache" / "huggingface",
    "Codex runtimes": HOME / ".codex" / "runtimes",
    "Claude caches": HOME / ".claude" / "cache",
    "Browser caches": HOME / "Library" / "Caches" / "Google",
}
FORBIDDEN_NAMES = {
    "Application Support",
    "docker",
    "volumes",
    "node_modules",
    "Documents",
}


def is_within(path: Path, root: Path) -> bool:
    """Resolve without following a leaf symlink and require path under root."""
    candidate = path.absolute()
    base = root.absolute()
    try:
        candidate.relative_to(base)
    except ValueError:
        return False
    # Existing parents must resolve beneath the approved root. Leaf symlinks rejected.
    if candidate.is_symlink():
        return False
    try:
        resolved = candidate.resolve(strict=False)
        resolved_base = base.resolve(strict=False)
    except OSError:
        return False
    try:
        resolved.relative_to(resolved_base)
    except ValueError:
        return False
    return not any(part in FORBIDDEN_NAMES for part in candidate.parts)


def validate_target(path: Path, category: str) -> bool:
    """Accept only a path equal to the hard-coded root for a SAFE category."""
    allowed = SAFE_PATHS.get(category)
    if allowed is None or path.absolute() != allowed.absolute():
        return False
    return is_within(path, HOME)


def safe_size(path: Path) -> int:
    """Calculate size without following symlinks."""
    if path.is_symlink() or not path.exists():
        return 0
    if path.is_file():
        return path.stat(follow_symlinks=False).st_size
    total = 0
    for item in path.iterdir():
        if item.is_symlink():
            continue
        if item.is_file():
            total += item.stat(follow_symlinks=False).st_size
        elif item.is_dir():
            total += safe_size(item)
    return total
