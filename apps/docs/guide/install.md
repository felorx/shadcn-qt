# Install

## Python

From the repository:

```bash
cd packages/python
pip install -e ".[pyside6]"
# or: pip install -e ".[pyqt6]" | ".[pyside2]" | ".[pyqt5]"
```

Install the recommended Qt Designer integration (includes PySide6):

```bash
pip install -e ".[designer]"
qtshadcn-designer
```

Force a binding explicitly:

```bash
export QTSHADCN_QT_BINDING=PySide6
```

Run a minimal window:

```bash
python ../../examples/python_minimal/run_pyside6.py
```

Run a form created with Qt Designer:

```bash
python ../../examples/python_designer/run.py
```

**Note:** PyQt5 is GPL-licensed from Riverbank; evaluate license fit for closed-source apps separately from this library’s MIT license.

## C++

Point CMake at your Qt 5.15+ or Qt 6 installation:

```bash
cd examples/cpp_minimal
cmake -B build -DCMAKE_PREFIX_PATH=/path/to/Qt/6.x/<platform>
cmake --build build
./build/qtshadcn_cpp_minimal
```

The static library `QtShadcn` embeds generated QSS via Qt resources (`:/qtshadcn/base_light.qss`).

## Regenerate styles

After editing `packages/design-tokens/tokens.json`:

```bash
python tools/token-codegen/generate.py
```
