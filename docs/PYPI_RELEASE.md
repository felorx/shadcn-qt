# PyPI release runbook

## Names

The distribution name is `shadcn-qt` and the Python import package is
`shadcn_qt`:

```bash
pip install "shadcn-qt[pyside6]"
```

```python
import shadcn_qt
```

The published runtime requires Python 3.9 or newer. CI covers Python 3.9,
3.11, and 3.13; use Python 3.11 or newer for the release tooling itself.

Version 0.1.0 was first published on 2026-08-14 (Asia/Shanghai) and is available
at [pypi.org/project/shadcn-qt](https://pypi.org/project/shadcn-qt/). Do not
publish a second distribution name for the same release. The project metadata
and documentation must continue to state that this is an independent Qt
implementation and is not affiliated with the upstream shadcn project.

Version 0.2.0 adds the complete component and native QtWidgets galleries,
classic `new-york` + Zinc visual alignment, reversible native-widget adoption,
visual screenshot regression, font-independent vector glyphs, and the
Chrome-style `TabPane`. See `CHANGELOG.md` for the release notes.

Initial release files:

| File | SHA-256 |
| --- | --- |
| `shadcn_qt-0.1.0-py3-none-any.whl` | `0fca0031d171307156a6013ee62dc83b8966ed3eb918f0805df424c2b4126fd5` |
| `shadcn_qt-0.1.0.tar.gz` | `64b65840019e5d1a11220fad0c94eb48b0f76d00b5e32e1583ab345bfa5563c2` |

## One-time publisher setup

1. Keep `https://github.com/felorx/shadcn-qt` public. Confirm the source, issue,
   and documentation URLs in `packages/python/pyproject.toml` resolve. The
   commercial URL temporarily points to the Felorx homepage; replace it with a
   dedicated sales page when one is available.
2. Create protected GitHub environments named `testpypi` and `pypi`. Require a
   reviewer for `pypi`, restrict deployment branches/tags, and prevent
   self-review where the organization supports it.
3. On TestPyPI, configure a Trusted Publisher for project `shadcn-qt`, the
   exact GitHub owner/repository, workflow `testpypi.yml`, and environment
   `testpypi`.
4. On PyPI, configure the existing `shadcn-qt` project with workflow
   `release.yml` and environment `pypi` as its Trusted Publisher.
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
python tools/check_branding.py
python tools/check_licenses.py
python tools/check_versions.py
python tools/check_release_readiness.py
python tools/check_core_boundary.py
python -m pytest packages/python/tests -q
python -m pip install --upgrade build twine
python -m build packages/python --outdir dist
python -m twine check --strict dist/*
python tools/check_python_dist.py dist
```

The public wheel must contain only the `shadcn_qt.pro` compatibility bridge.
The release fails if `shadcn_qt_pro`, a private signing key, or a customer
license certificate appears in the Core repository or distribution.

Inspect the diff, update the version in both `packages/python/pyproject.toml`
and `packages/cpp/shadcn_qt/CMakeLists.txt`, then update release notes before
tagging. `tools/check_versions.py` rejects mismatches. Never reuse a version
already uploaded to PyPI; PyPI release files are immutable.

## TestPyPI and production

The 0.1.0 project registration used a local PyPI API token after all release
checks and an isolated wheel smoke test. Future releases must use the Trusted
Publishing workflow after the GitHub environments and PyPI publisher are
configured; do not make local token uploads the normal release path.

Run the `testpypi` workflow manually first. Install its artifact in a clean
environment without pulling Qt dependencies from TestPyPI:

```bash
python -m pip install PySide6
python -m pip install --index-url https://test.pypi.org/simple \
  --no-deps shadcn-qt==0.2.0
```

After verification, create and push the exact version tag:

```bash
git tag -s v0.2.0 -m "shadcn-qt 0.2.0"
git push origin v0.2.0
```

The `release.yml` workflow verifies that the tag equals `v<package-version>`,
runs tests, builds one wheel and one sdist, checks their metadata and legal
files, and publishes through OIDC. The protected `pypi` environment is the
manual approval gate.

After publication, verify the PyPI metadata and install in clean PySide6 and
PyQt environments. Prefer yanking a broken release and publishing a new patch
version over deleting files. Record the exact package hashes and Order Form
agreement version used for commercial customers.
