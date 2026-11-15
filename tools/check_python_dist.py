"""Validate shadcn-qt wheel/sdist metadata and required legal files."""

from __future__ import annotations

import argparse
import re
import sys
import tarfile
from email.parser import BytesParser
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

DIST_NAME = "shadcn-qt"
NORMALIZED_DIST_NAME = "shadcn_qt"
EXPECTED_LICENSE = "GPL-3.0-only OR LicenseRef-Shadcn-Qt-Commercial"
EXPECTED_REQUIRES_PYTHON = ">=3.9"
EXPECTED_DESIGNER_ENTRY_POINT = (
    "shadcn-qt-designer = shadcn_qt.designer.launcher:main"
)
REQUIRED_LICENSE_BASENAMES = {
    "LICENSE",
    "NOTICE.md",
    "GPL-3.0-only.txt",
    "LicenseRef-Shadcn-Qt-Commercial.txt",
}
PUBLIC_PRO_BRIDGE = "shadcn_qt/pro/__init__.py"
PRIVATE_PACKAGE_PREFIX = "shadcn_qt_pro/"


def project_version(project_file: Path) -> str:
    match = re.search(
        r'^version\s*=\s*"([^"]+)"\s*$',
        project_file.read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if not match:
        raise ValueError(f"version not found in {project_file}")
    return match.group(1)


def validate_wheel(path: Path, version: str) -> list[str]:
    failures: list[str] = []
    expected_prefix = f"{NORMALIZED_DIST_NAME}-{version}-"
    if not path.name.startswith(expected_prefix):
        failures.append(f"unexpected wheel filename: {path.name}")

    with ZipFile(path) as archive:
        names = archive.namelist()
        metadata_names = [name for name in names if name.endswith(".dist-info/METADATA")]
        if len(metadata_names) != 1:
            return failures + [f"expected one METADATA in {path}, got {metadata_names}"]
        metadata = BytesParser().parsebytes(archive.read(metadata_names[0]))
        if metadata.get("Name") != DIST_NAME:
            failures.append(f"wheel Name is {metadata.get('Name')!r}, expected {DIST_NAME!r}")
        if metadata.get("Version") != version:
            failures.append(
                f"wheel Version is {metadata.get('Version')!r}, expected {version!r}"
            )
        if metadata.get("License-Expression") != EXPECTED_LICENSE:
            failures.append(
                "wheel License-Expression is "
                f"{metadata.get('License-Expression')!r}, expected {EXPECTED_LICENSE!r}"
            )
        if metadata.get("Requires-Python") != EXPECTED_REQUIRES_PYTHON:
            failures.append(
                "wheel Requires-Python is "
                f"{metadata.get('Requires-Python')!r}, expected "
                f"{EXPECTED_REQUIRES_PYTHON!r}"
            )

        license_basenames = {
            PurePosixPath(name).name
            for name in names
            if ".dist-info/licenses/" in name
        }
        missing = REQUIRED_LICENSE_BASENAMES - license_basenames
        if missing:
            failures.append(f"wheel is missing license files: {sorted(missing)}")
        if not any(name == "shadcn_qt/__init__.py" for name in names):
            failures.append("wheel does not contain the shadcn_qt import package")
        if "shadcn_qt/py.typed" not in names:
            failures.append(
                "wheel does not ship the shadcn_qt/py.typed marker (PEP 561)"
            )
        if PUBLIC_PRO_BRIDGE not in names:
            failures.append("wheel does not contain the public Pro compatibility bridge")
        leaked_private_files = [
            name for name in names if name.startswith(PRIVATE_PACKAGE_PREFIX)
        ]
        if leaked_private_files:
            failures.append(
                "public wheel contains private Pro implementation files: "
                f"{leaked_private_files}"
            )
        entry_point_names = [
            name for name in names if name.endswith(".dist-info/entry_points.txt")
        ]
        if len(entry_point_names) != 1:
            failures.append(
                f"expected one entry_points.txt in {path}, got {entry_point_names}"
            )
        else:
            entry_points = archive.read(entry_point_names[0]).decode("utf-8")
            if EXPECTED_DESIGNER_ENTRY_POINT not in entry_points:
                failures.append(
                    "wheel does not declare the shadcn-qt-designer entry point"
                )
    return failures


def validate_sdist(path: Path, version: str) -> list[str]:
    failures: list[str] = []
    expected = f"{NORMALIZED_DIST_NAME}-{version}.tar.gz"
    if path.name != expected:
        failures.append(f"unexpected sdist filename: {path.name}; expected {expected}")

    with tarfile.open(path, "r:gz") as archive:
        names = archive.getnames()
        basenames = {PurePosixPath(name).name for name in names}
        missing = REQUIRED_LICENSE_BASENAMES - basenames
        if missing:
            failures.append(f"sdist is missing license files: {sorted(missing)}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist_dir", type=Path)
    parser.add_argument(
        "--tag",
        help="release tag; when supplied it must equal v<project version>",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    version = project_version(root / "packages" / "python" / "pyproject.toml")
    failures: list[str] = []

    if args.tag and args.tag != f"v{version}":
        failures.append(f"tag {args.tag!r} does not match package version v{version}")

    wheels = sorted(args.dist_dir.glob("*.whl"))
    sdists = sorted(args.dist_dir.glob("*.tar.gz"))
    if len(wheels) != 1:
        failures.append(f"expected one wheel, found {[path.name for path in wheels]}")
    else:
        failures.extend(validate_wheel(wheels[0], version))
    if len(sdists) != 1:
        failures.append(f"expected one sdist, found {[path.name for path in sdists]}")
    else:
        failures.extend(validate_sdist(sdists[0], version))

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"validated {DIST_NAME} {version} wheel and sdist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
