"""Typer CLI for scanning and conservative cleanup."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from mac_cleaner.cleaners.operations import cleanup
from mac_cleaner.scanner import Candidate, scan
from mac_cleaner.utils import configure_logging, format_bytes, free_bytes

app = typer.Typer(help="Conservative cache cleanup for macOS.", no_args_is_help=True)
console = Console()


def show(items: list[Candidate]) -> None:
    table = Table("Category", "Cache", "Size", "Location")
    for item in items:
        table.add_row(item.category, item.name, format_bytes(item.size), str(item.path))
    console.print(table)
    reclaimable = sum(item.size for item in items if item.category == "SAFE")
    console.print(f"Estimated reclaimable space (SAFE): {format_bytes(reclaimable)}")


@app.command("scan")
def scan_command() -> None:
    """Inspect known cache locations and report sizes."""
    show(scan())
    console.print(f"Free disk space: {format_bytes(free_bytes())}")


@app.command("clean-safe")
def clean_safe(
    apply: bool = typer.Option(False, "--apply", help="Run approved cleanup commands."),
) -> None:
    """Preview SAFE categories, or clean them with --apply."""
    items = [item for item in scan() if item.category == "SAFE"]
    show(items)
    if not apply:
        console.print("Dry run: no files or caches changed. Pass --apply to clean.", style="yellow")
        return
    if typer.prompt("Type CLEAN to confirm", default="", show_default=False) != "CLEAN":
        console.print("Cancelled.")
        raise typer.Exit()
    logger = configure_logging()
    before = free_bytes()
    for item in items:
        ok, message = cleanup(item.name, logger)
        console.print(f"{'✓' if ok else '✗'} {item.name}: {message}")
    after = free_bytes()
    console.print(f"Free disk space: {format_bytes(before)} before → {format_bytes(after)} after")


@app.command()
def interactive() -> None:
    """Review each SAFE cleanup candidate individually."""
    items = [item for item in scan() if item.category == "SAFE"]
    show(items)
    logger = configure_logging()
    before = free_bytes()
    for item in items:
        if item.size <= 0:
            continue
        if typer.confirm(f"Clean {item.name} ({format_bytes(item.size)})?", default=False):
            if typer.confirm(f"Confirm cleanup of {item.name}?", default=False):
                ok, message = cleanup(item.name, logger)
                console.print(f"{'✓' if ok else '✗'} {item.name}: {message}")
    console.print(
        f"Free disk space: {format_bytes(before)} before → {format_bytes(free_bytes())} after"
    )


if __name__ == "__main__":
    app()
