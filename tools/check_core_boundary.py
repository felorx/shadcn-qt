"""Prevent private Pro code, credentials, and entitlements entering Core."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE_PRO_BRIDGE = Path("packages/python/shadcn_qt/pro/__init__.py")
SELF = Path("tools/check_core_boundary.py")
PRIVATE_PATH_PREFIXES = (
    "packages/python/shadcn_qt_pro/",
    "packages/python/shadcn_qt_pro.",
    "customer-licenses/",
    "license-certificates/",
)
PRIVATE_SUFFIXES = (".key", ".p12", ".pfx", ".license.json")
PRIVATE_KEY_MARKERS = (
    b"-----begin private key-----",
    b"-----begin encrypted private key-----",
    b"-----begin openssh private key-----",
)


def repository_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
    )
    return [ROOT / os.fsdecode(item) for item in output.split(b"\0") if item]


def main() -> int:
    failures: list[str] = []
    files = repository_files()
    relative_files = {path.relative_to(ROOT) for path in files}

    if CORE_PRO_BRIDGE not in relative_files:
        failures.append(f"missing Core-to-Pro bridge: {CORE_PRO_BRIDGE}")

    for path in files:
        relative = path.relative_to(ROOT)
        normalized = relative.as_posix().lower()
        if any(normalized.startswith(prefix) for prefix in PRIVATE_PATH_PREFIXES):
            failures.append(f"private Pro path in public repository: {relative}")
            continue
        if normalized.endswith(PRIVATE_SUFFIXES):
            failures.append(f"private key or entitlement file in Core: {relative}")
            continue
        if relative == CORE_PRO_BRIDGE:
            continue
        if normalized.startswith("packages/python/shadcn_qt/pro/"):
            failures.append(f"Pro implementation beside public bridge: {relative}")
            continue

        if relative == SELF:
            continue

        contents = path.read_bytes().lower()
        if any(marker in contents for marker in PRIVATE_KEY_MARKERS):
            failures.append(f"private signing key material in Core: {relative}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print("public Core contains only the Pro bridge and no private entitlement data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
