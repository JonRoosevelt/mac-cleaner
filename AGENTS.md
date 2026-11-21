# Project guidance

- Keep cleanup conservative. Never add a target without allowlist and safety tests.
- Actual cleanup requires `--apply` plus an explicit confirmation.
- Never use sudo, follow symlinks, or recursively delete arbitrary paths.
- Prefer official cleanup commands and test destructive behavior with mocked subprocesses.
- Run `pytest` and `ruff check .` after changes.
