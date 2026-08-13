"""Block public uploads until publisher identity and public URLs are real."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import tomllib

ROOT = Path(__file__).resolve().parents[1]
PROJECT_FILE = ROOT / "packages" / "python" / "pyproject.toml"
LICENSE_FILES = [ROOT / "LICENSE", ROOT / "packages" / "python" / "LICENSE"]
GENERIC_AUTHORS = {
    "",
    "shadcn-qt contributors",
    "shadcn-qt copyright holders",
}
GENERIC_COPYRIGHT_MARKERS = {
    "shadcn-qt copyright holders",
}
REQUIRED_URLS = {"Source", "Documentation", "Commercial"}


def valid_public_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    hostname = (parsed.hostname or "").lower()
    reserved = (
        not hostname
        or hostname == "localhost"
        or hostname.endswith((".example", ".invalid", ".localhost", ".test"))
        or hostname in {"example.com", "example.org", "example.net"}
    )
    return parsed.scheme == "https" and not reserved


def valid_remote(value: str) -> bool:
    lowered = value.lower()
    if not value or lowered.startswith(("/", "./", "../", "file://")):
        return False
    if any(marker in lowered for marker in ("example.com", ".invalid", "localhost")):
        return False
    return "://" in value or bool(re.match(r"^[^@\s]+@[^:\s]+:.+$", value))


def main() -> int:
    project = tomllib.loads(PROJECT_FILE.read_text(encoding="utf-8"))["project"]
    failures: list[str] = []

    authors = {
        str(author.get("name", "")).strip().lower()
        for author in project.get("authors", [])
    }
    if not authors or authors & GENERIC_AUTHORS:
        failures.append(
            "replace the generic [project].authors name with the public legal "
            "publisher or copyright owner"
        )

    generic_copyright_files = []
    for license_file in LICENSE_FILES:
        contents = license_file.read_text(encoding="utf-8").lower()
        if any(marker in contents for marker in GENERIC_COPYRIGHT_MARKERS):
            generic_copyright_files.append(str(license_file.relative_to(ROOT)))
    if generic_copyright_files:
        failures.append(
            "replace the generic copyright-holder text with the public legal "
            f"owner in {generic_copyright_files}"
        )

    urls = project.get("urls", {})
    missing_urls = REQUIRED_URLS - set(urls)
    if missing_urls:
        failures.append(f"add real [project.urls] entries: {sorted(missing_urls)}")
    for name in REQUIRED_URLS & set(urls):
        value = urls[name]
        if not valid_public_url(value):
            failures.append(f"{name} must be a public https URL, got {value!r}")
        elif name in {"Source", "Commercial"} and "pypi.org/project/" in value:
            failures.append(f"{name} must not point back to the PyPI project page")

    remote = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if not valid_remote(remote):
        failures.append("configure a real public git remote named origin")

    if failures:
        print("release is intentionally blocked:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print("publisher identity, public URLs, and origin remote are configured")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
