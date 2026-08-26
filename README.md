# shadcn-qt

[![CI](https://github.com/felorx/shadcn-qt/actions/workflows/ci.yml/badge.svg)](https://github.com/felorx/shadcn-qt/actions/workflows/ci.yml)
[![Python](https://img.shields.io/pypi/pyversions/shadcn-qt.svg?logo=python&logoColor=white)](https://pypi.org/project/shadcn-qt/)
[![Qt](https://img.shields.io/badge/Qt-5.15%2B%20%7C%206.x-41CD52?logo=qt&logoColor=white)](https://felorx.github.io/shadcn-qt/guide/install)
[![PyPI](https://img.shields.io/pypi/v/shadcn-qt.svg)](https://pypi.org/project/shadcn-qt/)
[![License](https://img.shields.io/badge/license-GPL--3.0--only%20OR%20Commercial-blue.svg)](LICENSE)

Qt / PyQt / PySide component and style primitives aligned with [shadcn/ui](https://ui.shadcn.com/) semantics: semantic design tokens, variants, composable widgets, global themes, and Qt Designer drag-and-drop integration.

shadcn-qt is an independent Qt implementation. It is not affiliated with or
endorsed by shadcn, Vercel, The Qt Company, or Riverbank Computing.
The project is published by [Felorx](https://felorx.com).

## Current status

- **Python:** PySide6, PyQt6, PySide2, and PyQt5 through one public API.
- **Widgets:** 66 public Python widgets covering the current shadcn/ui catalog and the Chrome-style `TabPane` Qt convenience, including dialogs, menus, forms, navigation, data display, charts, notifications, and conversation components.
- **Qt Designer:** the Python widgets can appear in a `shadcn-qt` Widget Box group, be dragged onto forms, laid out, and configured through native Qt properties.
- **Themes:** built-in light/dark themes, process-wide configuration, per-application overrides, JSON themes, custom QSS, radius, and font overrides.
- **Visual baseline:** classic shadcn/ui `new-york` geometry and states with the Zinc light/dark palette, including custom-painted selection controls and Qt-native overlay transitions.
- **Legacy adoption:** the complete native QtWidgets family receives component-specific or neutral fallback styling without changing existing classes.
- **C++:** Button, Input, Card, generated light/dark QSS, and CMake package support.

See [docs/STATUS.md](docs/STATUS.md) for the verified matrix and remaining parity work.
The exact geometry and translation rules are documented in the
[classic new-york + Zinc visual baseline](docs/STYLE_BASELINE.md).

## Layout

| Path | Description |
|------|-------------|
| `packages/design-tokens` | Source JSON for semantic colors and radius |
| `packages/python/shadcn_qt` | `shadcn-qt` PyPI distribution (PySide6 / PyQt6 / PySide2 / PyQt5) |
| `packages/cpp/shadcn_qt` | CMake library (Qt 5.15+ and Qt 6.x) |
| `tools/token-codegen` | Generates QSS, Python, and C++ theme artifacts |
| `apps/docs` | Documentation site |
| `examples` | Minimal Python and C++ samples |
| `skills/developing-shadcn-qt` | Vendor-neutral AI skill for repository development |

## Core and Pro

This public repository contains **shadcn-qt Core**. Core remains a complete,
usable package under either GPL-3.0-only or a commercial Core Order Form.

**shadcn-qt Pro** is a separately ordered, privately distributed add-on. Its
distribution name is `shadcn-qt-pro` and its import name is `shadcn_qt_pro`.
The public `shadcn_qt.pro` module is only a compatibility bridge and never
contains Pro implementation code. A commercial license for Core does not grant
Pro access; the customer's Order Form and signed license certificate identify
the Pro features, seats, covered versions, and update period.

See [Core and Pro architecture](docs/PRO.md) and [license tiers](docs/TIERS.md).

## Install the free Core package (Python)

shadcn-qt Core 0.2.6 is available from
[PyPI](https://pypi.org/project/shadcn-qt/). It is publicly downloadable at no
cost for GPL-3.0-compatible use; proprietary applications require a commercial
Core license. Pro is a separate private package.

Use a virtual environment (recommended on macOS/Homebrew Python):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

For a new application, install the `shadcn-qt` distribution with exactly one
Qt binding extra. Python uses the normalized import identifier `shadcn_qt`.
Python 3.9 or newer is required:

```bash
python -m pip install "shadcn-qt[pyside6]"
# or: pyqt6 | pyside2 | pyqt5
```

If an existing project already uses PySide or PyQt, keep that binding and avoid
changing it:

```bash
python -m pip install shadcn-qt
```

Confirm the installed release:

```bash
python -c "from importlib.metadata import version; print(version('shadcn-qt'))"
```

For an editable source checkout:

```bash
python -m pip install -e "./packages/python[pyside6,dev]"
```

Create and theme widgets:

```python
from shadcn_qt import (
    Button,
    Input,
    apply_theme,
    configure,
    configure_high_dpi,
)
from shadcn_qt._qt import QtWidgets

configure(theme="dark", colors={"primary": "#7c3aed"}, radius_base=9)
configure_high_dpi()  # before QApplication; preserves Windows 125%/150%/175%
app = QtWidgets.QApplication([])
apply_theme(app)

button = Button("Save", variant="outline", size="sm")
field = Input()
```

`radius_base` is the `md` corner radius in pixels. One value derives every
semantic component radius using the built-in `sm/md/lg/xl` ratio
`2/3 : 1 : 4/3 : 2`. For example, `radius_base=9` produces
`6px / 9px / 12px / 18px`. Use `radius={"xl": "20px"}` together with it
when one tier needs an explicit override. Circular and pill-shaped geometry
such as radio indicators, slider handles, and switch tracks remains circular.

Style an existing application without replacing its native widget classes:

```python
from shadcn_qt import apply_theme, enable_native_widget_styling

enable_native_widget_styling(app)
apply_theme(app, "dark")
```

The opt-in adapter covers the standard QtWidgets families, including forms,
item views, containers, dialogs, menus, toolbars, docks, and widgets created
later. QSS-inexpressible checkbox/radio glyphs and calendar cells receive
reversible Qt painting enhancements. Open the Gallery's **Native QtWidgets**
section to inspect four pages built only from stock Qt classes.

## Qt Designer

For the most predictable Designer plugin host, install the Designer extra and launch Designer through the shadcn-qt launcher:

```bash
pip install "shadcn-qt[designer]"
shadcn-qt-designer
```

The `shadcn-qt` group contains all 66 Python widgets. Properties such as `variant`, `shadcnSize`, `invalid`, `expanded`, `side`, `direction`, `chartType`, and `level` are editable in the Property Editor. Load the resulting form without a code-generation step:

```python
from shadcn_qt.designer import load_ui
window = load_ui("window.ui")
```

See [the Designer guide](apps/docs/guide/designer.md) and the runnable [Designer example](examples/python_designer/run.py).

Already have a PySide or PyQt application? Follow the [existing-project migration guide](apps/docs/guide/migration.md) to keep the current binding and `.ui` files, merge legacy QSS, and replace widgets incrementally.

Regenerate theme artifacts after editing tokens:

```bash
python tools/token-codegen/generate.py
```

Run the smoke example:

```bash
python examples/python_minimal/run_pyside6.py
```

Browse all 66 Core components with search, interactive states, and light/dark
theme switching:

```bash
python examples/python_gallery/run.py
```

The Gallery header includes a live base-radius control. You can also launch a
specific radius directly with `--radius-base 12`.

See the [component gallery guide](examples/python_gallery/README.md) for direct
component selection and screenshot options.

## Quick start (C++)

```bash
cmake -S packages/cpp/shadcn_qt -B build -DCMAKE_PREFIX_PATH=/path/to/Qt/6.x/macos
cmake --build build
```

Use Qt 5.15 by pointing `CMAKE_PREFIX_PATH` at a Qt5 kit; the same `CMakeLists.txt` selects Qt5 or Qt6 automatically.
Installed packages expose version `0.2.6`, so downstream projects can require
`find_package(ShadcnQt 0.2 CONFIG REQUIRED)`.

## Docs

Browse the [VitePress documentation](https://felorx.github.io/shadcn-qt/),
or see its source in `apps/docs`. The repository also includes the
[migration guide](apps/docs/guide/migration.md),
[licensing guide](docs/COMMERCIAL.md), [PyPI release runbook](docs/PYPI_RELEASE.md),
[Core and Pro architecture](docs/PRO.md), [docs/STATUS.md](docs/STATUS.md), and
[docs/TIERS.md](docs/TIERS.md). Release changes are recorded in
[CHANGELOG.md](CHANGELOG.md). AI agents can use the repository development
skill by following the [AI skill installation guide](docs/AI_SKILL_INSTALL.md).

## License

Current releases are offered under your choice of:

- **GPL-3.0-only** for GPL-compatible open-source use; or
- the **shadcn-qt Commercial License** for proprietary applications covered by
  a paid Order Form.

There are no runtime or per-end-user royalties in the standard commercial
terms. Licenses are counted by active developers. Downloading from PyPI alone
does not create a commercial entitlement. See [LICENSE](LICENSE),
[commercial licensing](docs/COMMERCIAL.md), and the
[third-party license matrix](docs/THIRD_PARTY_LICENSES.md).

The shadcn-qt license does not include Qt, PySide, or PyQt licenses.
