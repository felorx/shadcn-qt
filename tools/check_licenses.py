"""Fail when repository and Python-distribution license files diverge."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_ROOT = ROOT / "packages" / "python"
LICENSE_FILES = (
    "LICENSE",
    "NOTICE.md",
    "LICENSES/GPL-3.0-only.txt",
    "LICENSES/LicenseRef-Shadcn-Qt-Commercial.txt",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    for relative in LICENSE_FILES:
        repository_file = ROOT / relative
        package_file = PYTHON_ROOT / relative
        if not repository_file.is_file():
            failures.append(f"missing repository file: {repository_file}")
            continue
        if not package_file.is_file():
            failures.append(f"missing package file: {package_file}")
            continue
        if digest(repository_file) != digest(package_file):
            failures.append(
                f"license copy differs: {repository_file} != {package_file}"
            )

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"license files are synchronized ({len(LICENSE_FILES)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
