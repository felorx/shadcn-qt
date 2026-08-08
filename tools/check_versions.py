"""Ensure the Python and C++ distributions use one release version."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = ROOT / "packages" / "python" / "pyproject.toml"
CMAKE_PROJECT = ROOT / "packages" / "cpp" / "shadcn_qt" / "CMakeLists.txt"


def extract_version(path: Path, pattern: str, label: str) -> str:
    match = re.search(pattern, path.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise ValueError(f"could not find {label} version in {path}")
    return match.group(1)


def main() -> int:
    python_version = extract_version(
        PYPROJECT,
        r'^version\s*=\s*"([^"]+)"\s*$',
        "Python",
    )
    cpp_version = extract_version(
        CMAKE_PROJECT,
        r"^project\(ShadcnQt\s+VERSION\s+([^\s)]+)\s+LANGUAGES\s+CXX\)$",
        "C++",
    )

    if python_version != cpp_version:
        print(
            f"version mismatch: Python={python_version}, C++={cpp_version}",
            file=sys.stderr,
        )
        return 1

    print(f"Python and C++ versions are synchronized at {python_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
