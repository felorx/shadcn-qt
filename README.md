# qtshadcn

Qt / PyQt / PySide component and style primitives aligned with [shadcn/ui](https://ui.shadcn.com/) semantics (design tokens, variants, composable widgets).

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

See `apps/docs` (VitePress) and [docs/TIERS.md](docs/TIERS.md) for Community vs Pro scope.

## License

MIT (see [LICENSE](LICENSE)).
