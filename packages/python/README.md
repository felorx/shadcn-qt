# shadcn-qt (Python)

The free Core package is published at
[PyPI](https://pypi.org/project/shadcn-qt/). The distribution name is
`shadcn-qt`; its normalized Python import name is `shadcn_qt`. Python 3.9 or
newer is required.

For a new environment, install with exactly **one** Qt binding extra:

This is an independent Qt implementation and is not affiliated with or
endorsed by the upstream shadcn project. It is published by
[Felorx](https://felorx.com).

```bash
python -m pip install "shadcn-qt[pyside6]"
# or: pyqt6 | pyside2 | pyqt5
```

If an existing project already has PySide or PyQt, preserve it and install Core
without a binding extra:

```bash
python -m pip install shadcn-qt
```

Verify the installed version with:

```bash
python -c "from importlib.metadata import version; print(version('shadcn-qt'))"
```

For source development, use
`python -m pip install -e ".[pyside6,dev]"` in this directory.

Regenerate styles after editing `packages/design-tokens/tokens.json`:

```bash
python ../../tools/token-codegen/generate.py
```

## Global and custom themes

```python
from shadcn_qt import apply_theme, configure, create_theme

brand = create_theme(
    "brand",
    base="light",
    colors={"primary": "#7c3aed", "ring": "#8b5cf6"},
    radius={"md": "10px"},
)
configure(theme=brand, extra_qss="QWidget#sidebar { border: none; }")
apply_theme()  # uses the current QApplication
```

JSON theme files can be loaded with `load_theme("brand.json")`.

## Existing native widgets

Apply full default shadcn-qt styling to the complete existing and future QtWidgets family without replacing classes. Known controls use component-specific rules; uncommon or third-party QWidget subclasses receive a neutral themed fallback:

```python
from shadcn_qt import apply_theme, enable_native_widget_styling

enable_native_widget_styling(app)
apply_theme(app, "light")
```

Use `adopt_native_widgets(page)` for one subtree, and `disable_native_widget_styling(app)` to remove unchanged adapter defaults. Set `shadcn_qt_native_styling=False` on custom-painted or third-party widgets that should be left alone.

## Qt Designer

Install the recommended plugin host, then launch Designer with the registration path already configured:

```bash
pip install "shadcn-qt[designer]"
shadcn-qt-designer
```

Use `from shadcn_qt.designer import load_ui` to load the saved form under PySide or PyQt.

The public package exports 65 Qt-native classes covering the current named shadcn/ui catalog. Compound widgets retain normal Qt signals, models, layouts, and Designer-editable properties.

## Core and Pro

This distribution is shadcn-qt Core. The separately ordered private
`shadcn-qt-pro` distribution uses the `shadcn_qt_pro` import name. The
`shadcn_qt.pro` namespace in Core only forwards to that package when it is
installed; no Pro implementation or customer entitlement is included in this
wheel. Core commercial rights and Pro access are separate Order Form items.

## License

Core is publicly downloadable at no cost under GPL-3.0-only. Proprietary
projects need a valid shadcn-qt commercial Order Form instead. Installing from
PyPI does not grant commercial rights. The commercial license does not include
the separate Qt, PySide, or PyQt licenses. See the `LICENSE`, `LICENSES`, and
`NOTICE.md` files included in every wheel and source distribution.
