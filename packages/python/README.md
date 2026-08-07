# qtshadcn (Python)

Install with exactly **one** Qt binding extra:

```bash
pip install -e ".[pyside6]"
# or: pyqt6 | pyside2 | pyqt5
```

Regenerate styles after editing `packages/design-tokens/tokens.json`:

```bash
python ../../tools/token-codegen/generate.py
```

## Global and custom themes

```python
from qtshadcn import apply_theme, configure, create_theme

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

Apply full default qtshadcn styling to the complete existing and future QtWidgets family without replacing classes. Known controls use component-specific rules; uncommon or third-party QWidget subclasses receive a neutral themed fallback:

```python
from qtshadcn import apply_theme, enable_native_widget_styling

enable_native_widget_styling(app)
apply_theme(app, "light")
```

Use `adopt_native_widgets(page)` for one subtree, and `disable_native_widget_styling(app)` to remove unchanged adapter defaults. Set `qtshadcn_native_styling=False` on custom-painted or third-party widgets that should be left alone.

## Qt Designer

Install the recommended plugin host, then launch Designer with the registration path already configured:

```bash
pip install -e ".[designer]"
qtshadcn-designer
```

Use `from qtshadcn.designer import load_ui` to load the saved form under PySide or PyQt.

The public package exports 65 Qt-native classes covering the current named shadcn/ui catalog. Compound widgets retain normal Qt signals, models, layouts, and Designer-editable properties.
