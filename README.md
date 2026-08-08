# shadcn-qt

Qt / PyQt / PySide component and style primitives aligned with [shadcn/ui](https://ui.shadcn.com/) semantics: semantic design tokens, variants, composable widgets, global themes, and Qt Designer drag-and-drop integration.

shadcn-qt is an independent Qt implementation. It is not affiliated with or
endorsed by shadcn, Vercel, The Qt Company, or Riverbank Computing.
The project is published by [Felorx](https://felorx.com).

## Current status

- **Python:** PySide6, PyQt6, PySide2, and PyQt5 through one public API.
- **Widgets:** 65 public Python widgets covering the current shadcn/ui catalog with Qt-native mappings, including dialogs, menus, forms, navigation, data display, charts, notifications, and conversation components.
- **Qt Designer:** the Python widgets can appear in a `shadcn-qt` Widget Box group, be dragged onto forms, laid out, and configured through native Qt properties.
- **Themes:** built-in light/dark themes, process-wide configuration, per-application overrides, JSON themes, custom QSS, radius, and font overrides.
- **Legacy adoption:** the complete native QtWidgets family receives component-specific or neutral fallback styling without changing existing classes.
- **C++:** Button, Input, Card, generated light/dark QSS, and CMake package support.

See [docs/STATUS.md](docs/STATUS.md) for the verified matrix and remaining parity work.

## Layout

| Path | Description |
|------|-------------|
| `packages/design-tokens` | Source JSON for semantic colors and radius |
| `packages/python/shadcn_qt` | `shadcn-qt` PyPI distribution (PySide6 / PyQt6 / PySide2 / PyQt5) |
| `packages/cpp/shadcn_qt` | CMake library (Qt 5.15+ and Qt 6.x) |
| `tools/token-codegen` | Generates QSS, Python, and C++ theme artifacts |
| `apps/docs` | Documentation site |
| `examples` | Minimal Python and C++ samples |

## Quick start (Python)

Use a virtual environment (recommended on macOS/Homebrew Python):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the `shadcn-qt` distribution with one Qt binding extra. Python uses
the normalized import identifier `shadcn_qt`. Python 3.9 or newer is required:

```bash
pip install "shadcn-qt[pyside6]"
# or: pyqt6 | pyside2 | pyqt5
```

For an editable source checkout:

```bash
pip install -e "./packages/python[pyside6]"
```

Create and theme widgets:

```python
from shadcn_qt import Button, Input, apply_theme, configure
from shadcn_qt._qt import QtWidgets

configure(theme="dark", colors={"primary": "#7c3aed"}, radius={"md": "10px"})
app = QtWidgets.QApplication([])
apply_theme(app)

button = Button("Save", variant="outline", size="sm")
field = Input()
```

Style an existing application without replacing its native widget classes:

```python
from shadcn_qt import apply_theme, enable_native_widget_styling

enable_native_widget_styling(app)
apply_theme(app, "dark")
```

## Qt Designer

For the most predictable Designer plugin host, install the Designer extra and launch Designer through the shadcn-qt launcher:

```bash
pip install "shadcn-qt[designer]"
shadcn-qt-designer
```

The `shadcn-qt` group contains all 65 Python widgets. Properties such as `variant`, `shadcnSize`, `invalid`, `expanded`, `side`, `direction`, `chartType`, and `level` are editable in the Property Editor. Load the resulting form without a code-generation step:

```python
from shadcn_qt.designer import load_ui
window = load_ui("window.ui")
```

See [the Designer guide](apps/docs/guide/designer.md) and the runnable [Designer example](examples/python_designer/run.py).

Already have a PySide or PyQt application? Follow the [existing-project migration guide](apps/docs/guide/migration.md) to keep the current binding and `.ui` files, merge legacy QSS, and replace widgets incrementally.

Regenerate theme artifacts after editing tokens:

```bash
python ../../tools/token-codegen/generate.py
```

Run the smoke example:

```bash
python ../../examples/python_minimal/run_pyside6.py
```

## Quick start (C++)

```bash
cmake -S packages/cpp/shadcn_qt -B build -DCMAKE_PREFIX_PATH=/path/to/Qt/6.x/macos
cmake --build build
```

Use Qt 5.15 by pointing `CMAKE_PREFIX_PATH` at a Qt5 kit; the same `CMakeLists.txt` selects Qt5 or Qt6 automatically.
Installed packages expose version `0.1.0`, so downstream projects can require
`find_package(ShadcnQt 0.1 CONFIG REQUIRED)`.

## Docs

See `apps/docs` (VitePress), the [migration guide](apps/docs/guide/migration.md),
[licensing guide](docs/COMMERCIAL.md), [PyPI release runbook](docs/PYPI_RELEASE.md),
[docs/STATUS.md](docs/STATUS.md), and [docs/TIERS.md](docs/TIERS.md).

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
