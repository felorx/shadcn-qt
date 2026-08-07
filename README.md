# qtshadcn

Qt / PyQt / PySide component and style primitives aligned with [shadcn/ui](https://ui.shadcn.com/) semantics: semantic design tokens, variants, composable widgets, global themes, and Qt Designer drag-and-drop integration.

## Current status

- **Python:** PySide6, PyQt6, PySide2, and PyQt5 through one public API.
- **Widgets:** 65 public Python widgets covering the current shadcn/ui catalog with Qt-native mappings, including dialogs, menus, forms, navigation, data display, charts, notifications, and conversation components.
- **Qt Designer:** the Python widgets can appear in a `qtshadcn` Widget Box group, be dragged onto forms, laid out, and configured through native Qt properties.
- **Themes:** built-in light/dark themes, process-wide configuration, per-application overrides, JSON themes, custom QSS, radius, and font overrides.
- **Legacy adoption:** existing native Qt widgets can receive full default component styling without changing their classes.
- **C++:** Button, Input, Card, generated light/dark QSS, and CMake package support.

See [docs/STATUS.md](docs/STATUS.md) for the verified matrix and remaining parity work.

## Layout

| Path | Description |
|------|-------------|
| `packages/design-tokens` | Source JSON for semantic colors and radius |
| `packages/python/qtshadcn` | `pip install` package (PySide6 / PyQt6 / PySide2 / PyQt5) |
| `packages/cpp/qtshadcn` | CMake library (Qt 5.15+ and Qt 6.x) |
| `tools/token-codegen` | Generates QSS, Python, and C++ theme artifacts |
| `apps/docs` | Documentation site |
| `examples` | Minimal Python and C++ samples |

## Quick start (Python)

Use a virtual environment (recommended on macOS/Homebrew Python):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install one Qt binding extra, then the package from the repo root:

```bash
cd packages/python
pip install -e ".[pyside6]"
```

Create and theme widgets:

```python
from qtshadcn import Button, Input, apply_theme, configure
from qtshadcn._qt import QtWidgets

configure(theme="dark", colors={"primary": "#7c3aed"}, radius={"md": "10px"})
app = QtWidgets.QApplication([])
apply_theme(app)

button = Button("Save", variant="outline", size="sm")
field = Input()
```

Style an existing application without replacing its native widget classes:

```python
from qtshadcn import apply_theme, enable_native_widget_styling

enable_native_widget_styling(app)
apply_theme(app, "dark")
```

## Qt Designer

For the most predictable Designer plugin host, install the Designer extra and launch Designer through qtshadcn:

```bash
pip install -e ".[designer]"
qtshadcn-designer
```

The `qtshadcn` group contains all 65 Python widgets. Properties such as `variant`, `shadcnSize`, `invalid`, `expanded`, `side`, `direction`, `chartType`, and `level` are editable in the Property Editor. Load the resulting form without a code-generation step:

```python
from qtshadcn.designer import load_ui
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
cmake -S packages/cpp/qtshadcn -B build -DCMAKE_PREFIX_PATH=/path/to/Qt/6.x/macos
cmake --build build
```

Use Qt 5.15 by pointing `CMAKE_PREFIX_PATH` at a Qt5 kit; the same `CMakeLists.txt` selects Qt5 or Qt6 automatically.

## Docs

See `apps/docs` (VitePress), the [migration guide](apps/docs/guide/migration.md), [docs/STATUS.md](docs/STATUS.md), and [docs/TIERS.md](docs/TIERS.md).

## License

MIT (see [LICENSE](LICENSE)).
