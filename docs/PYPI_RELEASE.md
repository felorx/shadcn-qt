# PyPI release runbook

## Names

The PyPI project name `qtshadcn` is already owned by an unrelated publisher.
This repository therefore uses the distribution name `shadcn-qt` and the
Python import package `shadcn_qt`:

```bash
pip install "shadcn-qt[pyside6]"
```

```python
import shadcn_qt
```

The published runtime requires Python 3.9 or newer. CI covers Python 3.9,
3.11, and 3.13; use Python 3.11 or newer for the release tooling itself.

Names such as `shadcn` and `shadcn-ui` were deliberately not selected: they
are broad enough to imply an official relationship with the upstream web
project. `shadcn-qt` describes both the design influence and the target UI
toolkit. The project metadata and documentation must continue to state that
this is an independent Qt implementation and is not affiliated with the
upstream shadcn project.

The `shadcn-qt` JSON endpoint returned “not found” during preparation on
2026-08-08, but PyPI can reserve or normalize names and availability is not
guaranteed until the project is registered. Recheck immediately before launch.
Do not upload this project to the unrelated `qtshadcn` PyPI project, and do not
publish a second distribution name for the same release.

## One-time publisher setup

1. Create and make public the configured repository at
   `https://github.com/felorx/shadcn-qt`. Confirm the source, issue, and
   documentation URLs in `packages/python/pyproject.toml` resolve after the
   initial push. The commercial URL temporarily points to the Felorx homepage;
   replace it with a dedicated sales page when one is available.
2. Create protected GitHub environments named `testpypi` and `pypi`. Require a
   reviewer for `pypi`, restrict deployment branches/tags, and prevent
   self-review where the organization supports it.
3. On TestPyPI, configure a Trusted Publisher for project `shadcn-qt`, the
   exact GitHub owner/repository, workflow `testpypi.yml`, and environment
   `testpypi`.
4. On PyPI, create a pending Trusted Publisher with workflow `release.yml` and
   environment `pypi`, or configure it on the project after a first authorized
   registration.
5. Enable two-factor authentication and give at least two trusted owners access
   to the PyPI project. Do not put PyPI passwords or long-lived API tokens in
   GitHub secrets when Trusted Publishing is available.

The upload workflows intentionally run `tools/check_release_readiness.py` and
require the Felorx publisher identity, public `Source`, `Documentation`, and
`Commercial` HTTPS URLs, and a real public `origin` remote. This prevents an
anonymous or misdirected commercial release. The checker cannot create the
GitHub repository or verify ownership, so confirm both before enabling Trusted
Publishing.

Official setup documentation:

- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
- [Publishing from GitHub Actions](https://docs.pypi.org/trusted-publishers/using-a-publisher/)
- [Trusted Publishing security model](https://docs.pypi.org/trusted-publishers/security-model/)

## Local release checks

Use Python 3.11+ for release tooling:

```bash
python tools/token-codegen/generate.py
python tools/check_licenses.py
python tools/check_versions.py
python tools/check_release_readiness.py
python -m pytest packages/python/tests -q
python -m pip install --upgrade build twine
python -m build packages/python --outdir dist
python -m twine check --strict dist/*
python tools/check_python_dist.py dist
```

Inspect the diff, update the version in both `packages/python/pyproject.toml`
and `packages/cpp/shadcn_qt/CMakeLists.txt`, then update release notes before
tagging. `tools/check_versions.py` rejects mismatches. Never reuse a version
already uploaded to PyPI; PyPI release files are immutable.

## TestPyPI and production

Run the `testpypi` workflow manually first. Install its artifact in a clean
environment without pulling Qt dependencies from TestPyPI:

```bash
python -m pip install PySide6
python -m pip install --index-url https://test.pypi.org/simple \
  --no-deps shadcn-qt==0.1.0
```

After verification, create and push the exact version tag:

```bash
git tag -s v0.1.0 -m "shadcn-qt 0.1.0"
git push origin v0.1.0
```

The `release.yml` workflow verifies that the tag equals `v<package-version>`,
runs tests, builds one wheel and one sdist, checks their metadata and legal
files, and publishes through OIDC. The protected `pypi` environment is the
manual approval gate.

After publication, verify the PyPI metadata and install in clean PySide6 and
PyQt environments. Prefer yanking a broken release and publishing a new patch
version over deleting files. Record the exact package hashes and Order Form
agreement version used for commercial customers.
