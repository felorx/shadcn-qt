# shadcn-qt (Python)

shadcn-qt Core 0.2.5 is published at
[PyPI](https://pypi.org/project/shadcn-qt/). The distribution name is
`shadcn-qt`; its normalized Python import name is `shadcn_qt`. Python 3.9 or
newer is required.

Core uses the classic shadcn/ui `new-york` visual profile with the Zinc
light/dark palette. `STYLE_PROFILE` and `BASE_COLOR` expose that identity to
applications and tooling.

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
    radius_base=9,
    radius={"xl": "20px"},
)
configure(theme=brand, extra_qss="QWidget#sidebar { border: none; }")
apply_theme()  # uses the current QApplication
```

JSON theme files can be loaded with `load_theme("brand.json")`.

`radius_base` is a single pixel value for the `md` tier. It derives
`sm/md/lg/xl` using `2/3 : 1 : 4/3 : 2`, so `radius_base=9` yields
`6px / 9px / 12px / 18px`. Explicit entries in `radius` take precedence.
Shape-defining circles and pills retain their geometry instead of being
distorted by the semantic surface radius.

## High-DPI startup

Configure DPI handling before creating `QApplication`. This keeps fractional
Windows display scales such as 125%, 150%, and 175% exact instead of allowing
Qt 5 to round them to a larger integer scale:

```python
from shadcn_qt import apply_theme, configure_high_dpi
from shadcn_qt._qt import QtWidgets

configure_high_dpi()
app = QtWidgets.QApplication([])
apply_theme(app, "light")
```

Qt 6 already enables high-DPI rendering; the initializer selects precise
fractional scaling. On Qt 5 it also enables high-DPI widgets and pixmaps. Do
not combine normal Windows display scaling with a production
`QT_SCALE_FACTOR`; Qt multiplies that override by the native scale.

## Existing native widgets

Apply full default shadcn-qt styling to the complete existing and future QtWidgets family without replacing classes. Known controls use component-specific rules; uncommon or third-party QWidget subclasses receive a neutral themed fallback:

```python
from shadcn_qt import apply_theme, enable_native_widget_styling

enable_native_widget_styling(app)
apply_theme(app, "light")
```

Use `adopt_native_widgets(page)` for one subtree, and `disable_native_widget_styling(app)` to remove unchanged adapter defaults. Set `shadcn_qt_native_styling=False` on custom-painted or third-party widgets that should be left alone.

Known QtWidgets receive dedicated `new-york` + Zinc rules. QSS-inexpressible
checkbox/radio glyphs, editor arrows, calendar cells, and elevation use
reversible adapter enhancements. The repository Gallery includes four pages
built exclusively from stock QtWidgets plus eight light/dark screenshot
baselines.

## Qt Designer

Install the recommended plugin host, then launch Designer with the registration path already configured:

```bash
pip install "shadcn-qt[designer]"
shadcn-qt-designer
```

Use `from shadcn_qt.designer import load_ui` to load the saved form under PySide or PyQt.

The public package exports 66 Qt-native classes covering the current named shadcn/ui catalog plus the Chrome-style `TabPane` convenience. Compound widgets retain normal Qt signals, models, layouts, and Designer-editable properties.

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
