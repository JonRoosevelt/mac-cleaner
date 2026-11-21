# mac-cleaner

`mac-cleaner` is a conservative macOS cache-cleaning CLI. It scans known cache locations, shows their sizes, and estimates reclaimable space. Scanning does not change files. Cleanup is a dry run unless you explicitly pass `--apply` and confirm.

## Install from this repository

Open Terminal in the repository folder (the folder containing `pyproject.toml`). Python 3.11 or newer is required.

Create an isolated Python environment and install the CLI:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

Keep that terminal open with `.venv` activated while using `mac-cleaner`. In a new terminal, go back to the repository folder and run `source .venv/bin/activate` again. No global or system Python installation is needed.

## Use it

Start with a read-only scan:

```sh
mac-cleaner scan
```

Preview the safe cleanup candidates and estimated reclaimable space:

```sh
mac-cleaner clean-safe
```

To run the approved cleanup commands, pass `--apply`, then type `CLEAN` when prompted:

```sh
mac-cleaner clean-safe --apply
```

To choose safe candidates one by one, run:

```sh
mac-cleaner interactive
```

The interactive command asks before each cleanup. Press Enter at a confirmation prompt to skip it. Cleanup logs go to `~/Library/Logs/mac-cleaner/cleanup.log`. The tool never uses `sudo`.

## What the categories mean

- **SAFE** — npm, pip, Yarn Classic v6, Jest, GitHub CLI `run-log-*.zip` files, UV, and the Go build cache. These are the only categories the cleanup commands can run. Official cleanup commands are used where available.
- **REVIEW** — Playwright, Homebrew, TypeScript, HuggingFace, Codex, Claude, browser, and other application caches. The tool reports known locations, but never cleans them.
- **PROTECTED** — Application Support, Docker volumes, databases, `node_modules`, projects, documents, settings, and user data. These are never cleanup candidates.

Sizes and reclaimable space are estimates; the amount of disk space actually freed may differ. Scans do not follow symlinks. GitHub CLI cleanup only removes regular, non-symlink `run-log-*.zip` files from its validated cache folder.

## Development

To install the development tools as well as the package, use this instead of `python -m pip install .`:

```sh
python -m pip install -e '.[dev]'
```

Then run:

```sh
pytest
ruff check .
ruff format --check .
```

See [AGENTS.md](AGENTS.md) for project safety rules. The project is MIT licensed.
