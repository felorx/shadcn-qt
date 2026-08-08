# Install

## Python

From PyPI (the distribution name is `shadcn-qt`; Python normalizes it to the
import identifier `shadcn_qt`; Python 3.9 or newer is required):

```bash
pip install "shadcn-qt[pyside6]"
# or: pyqt6 | pyside2 | pyqt5
```

From a source checkout:

```bash
pip install -e "./packages/python[pyside6]"
```

Install the recommended Qt Designer integration (includes PySide6):

```bash
pip install "shadcn-qt[designer]"
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

Run a form created with Qt Designer:

```bash
python ../../examples/python_designer/run.py
```

**License note:** current shadcn-qt releases are GPL-3.0-only or commercial.
PyQt5 and PyQt6 are separately GPLv3 or commercially licensed by Riverbank and
are not LGPL. PySide6 and Qt also retain their own terms. Read the
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
Its installed CMake package exposes version `0.1.0`; downstream projects may
use `find_package(ShadcnQt 0.1 CONFIG REQUIRED)`.

## Regenerate styles

After editing `packages/design-tokens/tokens.json`:

```bash
python tools/token-codegen/generate.py
```
