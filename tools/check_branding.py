"""Reject obsolete project names in tracked paths and file contents."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_MARKERS = tuple(
    b"qt" + separator + b"shadcn" for separator in (b"", b"-", b"_")
)


def repository_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
    )
    return [ROOT / os.fsdecode(item) for item in output.split(b"\0") if item]


def main() -> int:
    failures: list[str] = []
    for path in repository_files():
        relative = path.relative_to(ROOT)
        encoded_path = os.fsencode(relative).lower()
        if any(marker in encoded_path for marker in LEGACY_MARKERS):
            failures.append(f"obsolete project name in repository path: {relative}")
            continue

        contents = path.read_bytes().lower()
        if any(marker in contents for marker in LEGACY_MARKERS):
            failures.append(f"obsolete project name in repository file: {relative}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print("repository paths and files use the shadcn-qt project name")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
