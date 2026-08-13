# Publishing to PyPI

This repository publishes as `shadcn-qt`, while Python uses
`import shadcn_qt`. The distribution and import names are the only supported
public names. The runtime requires Python 3.9 or newer; the CI matrix covers
Python 3.9, 3.11, and 3.13.

Releases use PyPI Trusted Publishing rather than a stored API token:

1. configure protected GitHub environments `testpypi` and `pypi`;
2. register the exact repository/workflow/environment as Trusted Publishers;
3. run the manual TestPyPI workflow;
4. update the matching versions in `packages/python/pyproject.toml` and
   `packages/cpp/shadcn_qt/CMakeLists.txt`, then tag exactly `v<version>`;
5. approve the protected `pypi` deployment after tests and artifact checks.

The workflow validates GPL/commercial metadata and confirms that all license
files are inside both the wheel and sdist. See the repository's
`docs/PYPI_RELEASE.md` for one-time setup, commands, verification, and recovery.

Publisher metadata is configured for Felorx. Before the first upload, ensure
`https://github.com/felorx/shadcn-qt` exists publicly, configure its protected
environments and Trusted Publishers, and replace the temporary Felorx homepage
commercial link when a dedicated sales page is available.
