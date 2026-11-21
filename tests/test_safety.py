from pathlib import Path

from mac_cleaner.safety import SAFE_PATHS, is_within, safe_size, validate_target


def test_only_exact_allowlisted_targets_are_accepted() -> None:
    assert validate_target(SAFE_PATHS["npm"], "npm")
    assert not validate_target(Path.home() / "Documents", "npm")
    assert not validate_target(SAFE_PATHS["npm"] / "nested", "npm")
    assert not validate_target(SAFE_PATHS["npm"], "Application Support")


def test_forbidden_paths_cannot_be_cleaned() -> None:
    for forbidden in (
        Path.home() / "Library" / "Application Support",
        Path.home() / "Documents",
        Path.home() / "project" / "node_modules",
        Path.home() / "Library" / "Docker" / "volumes",
    ):
        assert not validate_target(forbidden, "npm")
        assert not is_within(forbidden, Path.home())


def test_size_does_not_follow_symlinks(tmp_path: Path) -> None:
    root = tmp_path / "cache"
    root.mkdir()
    payload = tmp_path / "outside"
    payload.write_bytes(b"secret" * 100)
    (root / "linked").symlink_to(payload)
    (root / "ordinary").write_bytes(b"abc")
    assert safe_size(root) == 3


def test_symlink_target_is_rejected(tmp_path: Path) -> None:
    actual = tmp_path / "actual"
    actual.mkdir()
    link = tmp_path / "cache-link"
    link.symlink_to(actual)
    assert not is_within(link, tmp_path)
