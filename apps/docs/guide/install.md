# Install

## Python

shadcn-qt Core 0.2.5 is published on
[PyPI](https://pypi.org/project/shadcn-qt/). The distribution name is
`shadcn-qt`; Python normalizes it to the import identifier `shadcn_qt`. Python
3.9 or newer is required.

### New environment

Create a virtual environment and install exactly one Qt binding extra:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install "shadcn-qt[pyside6]"
# or: pyqt6 | pyside2 | pyqt5
```

Choose the extra that matches the application: `pyside6`, `pyqt6`, `pyside2`,
or `pyqt5`. Do not install several binding extras in one environment.

### Existing PySide or PyQt project

Keep the project's current binding and install the base package without an
extra. This avoids upgrading or replacing Qt dependencies:

```bash
python -m pip install shadcn-qt
```

See the [existing-project migration guide](./migration.md) for explicit binding
selection and incremental adoption.

### Verify the installation

```bash
python -c "from importlib.metadata import version; print(version('shadcn-qt'))"
```

The command should print `0.2.5`. Then verify that the
selected binding and package import together:

```bash
python -c "import shadcn_qt; print(shadcn_qt.__version__)"
```

### Source development

From a source checkout:

```bash
python -m pip install -e "./packages/python[pyside6,dev]"
```

Install the recommended Qt Designer integration (includes PySide6):

```bash
python -m pip install "shadcn-qt[designer]"
shadcn-qt-designer
```

Force a binding explicitly:

```bash
export SHADCN_QT_BINDING=PySide6
```

Run a minimal window:

```bash
python ../../examples/python_minimal/run_pyside6.py
```

### Windows and high-DPI displays

Initialize high-DPI behavior before constructing `QApplication`:

```python
from shadcn_qt import configure_high_dpi
from shadcn_qt._qt import QtWidgets

configure_high_dpi()
app = QtWidgets.QApplication([])
```

This preserves fractional Windows scales such as 125%, 150%, and 175%. Qt 5
also receives the required high-DPI widget and pixmap attributes. Do not set
`QT_SCALE_FACTOR` in a normal production launch: Qt already reads the Windows
display scale, and the environment override would multiply it a second time.

Run a form created with Qt Designer:

```bash
python ../../examples/python_designer/run.py
```

Browse the complete 66-component interactive gallery from the repository root:

```bash
python examples/python_gallery/run.py
```

The gallery supports component search, category navigation, light/dark theme
switching, and real interactions for overlays, menus, and notifications.

### Guidance for AI coding assistants

Before installing, inspect the project imports and dependency files for
`PySide6`, `PyQt6`, `PySide2`, or `PyQt5`. If one binding is already selected,
install `shadcn-qt` without an extra. If none is selected, ask which binding the
developer wants; use `pyside6` only when the project has no binding constraint.
Never install multiple binding extras or claim that public Core installation
also installs Pro.

**License note:** Core is publicly downloadable at no cost under GPL-3.0-only.
A proprietary application requires a commercial Core Order Form. PyQt5 and
PyQt6 are separately GPLv3 or commercially licensed by Riverbank and are not
LGPL. PySide6 and Qt retain their own terms. Read the
[licensing guide](./licensing.md) before shipping a proprietary application.

## C++

Point CMake at your Qt 5.15+ or Qt 6 installation:

```bash
cd examples/cpp_minimal
cmake -B build -DCMAKE_PREFIX_PATH=/path/to/Qt/6.x/<platform>
cmake --build build
./build/shadcn_qt_cpp_minimal
```

The static library `ShadcnQt` embeds generated QSS via Qt resources (`:/shadcn_qt/base_light.qss`).
Its installed CMake package exposes version `0.2.5`; downstream projects may
use `find_package(ShadcnQt 0.2 CONFIG REQUIRED)`.

## Regenerate styles

After editing `packages/design-tokens/tokens.json`:

```bash
python tools/token-codegen/generate.py
```
