import logging
from pathlib import Path
from unittest.mock import Mock, patch

from mac_cleaner.cleaners.operations import cleanup
from mac_cleaner.safety import SAFE_PATHS


def test_unknown_category_is_rejected_without_execution() -> None:
    with patch("mac_cleaner.cleaners.operations.subprocess.run") as run:
        ok, _ = cleanup("Application Support", logging.getLogger("test"))
    assert not ok
    run.assert_not_called()


def test_gh_removes_only_run_log_zip_files(tmp_path: Path) -> None:
    cache = tmp_path / "gh"
    cache.mkdir()
    allowed = cache / "run-log-123.zip"
    allowed.write_bytes(b"zip")
    preserved = cache / "config.yml"
    preserved.write_text("user config")
    arbitrary = cache / "other.zip"
    arbitrary.write_bytes(b"zip")

    with (
        patch.dict(SAFE_PATHS, {"gh": cache}),
        patch("mac_cleaner.cleaners.operations.validate_target", return_value=True),
        patch("mac_cleaner.cleaners.operations.free_bytes", return_value=100),
    ):
        ok, _ = cleanup("gh", Mock())

    assert ok
    assert not allowed.exists()
    assert preserved.exists()
    assert arbitrary.exists()


def test_gh_does_not_unlink_symlink(tmp_path: Path) -> None:
    cache = tmp_path / "gh"
    cache.mkdir()
    target = tmp_path / "outside.zip"
    target.write_bytes(b"keep")
    (cache / "run-log-link.zip").symlink_to(target)
    with (
        patch.dict(SAFE_PATHS, {"gh": cache}),
        patch("mac_cleaner.cleaners.operations.validate_target", return_value=True),
        patch("mac_cleaner.cleaners.operations.free_bytes", return_value=100),
    ):
        ok, _ = cleanup("gh", Mock())
    assert ok
    assert target.exists()
