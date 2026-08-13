# Theming

shadcn-qt uses the same semantic vocabulary as shadcn/ui: `background`, `foreground`, `primary`, `secondary`, `muted`, `accent`, `destructive`, `border`, `input`, and `ring`. Widgets consume those roles instead of hard-coded brand colors.

The built-in visual profile is **classic `new-york` + Zinc**. `new-york`
defines component geometry, spacing, shadows, focus states, and interaction
rhythm; Zinc defines the neutral light/dark palette. This is the classic
registry profile, not one of the newer Vega/Nova/Maia presets. The repository's
[visual baseline](./visual-baseline.md) records the audited metrics
and official registry references.

## Apply a built-in theme

```python
from shadcn_qt import apply_theme
from shadcn_qt._qt import QtWidgets

app = QtWidgets.QApplication([])
apply_theme(app, "dark")
```

`apply_theme("dark")` is also valid after a `QApplication` exists.

## Style existing native Qt widgets

Existing projects can keep their `QPushButton`, `QLineEdit`, `QCheckBox`, and other standard widget classes. Enable compatibility mode before constructing the main window:

```python
from shadcn_qt import apply_theme, enable_native_widget_styling

app = QtWidgets.QApplication([])
enable_native_widget_styling(app)

window = MainWindow()
apply_theme(app, "dark")
```

The adapter covers the complete QtWidgets QWidget family, including editors, item views, scrollbars, toolbars, docks, dialogs, containers, and dynamically created widgets. Known controls receive component-specific QSS; unknown QWidget subclasses receive a neutral theme fallback. Explicit component properties are preserved. Use `shadcn_qt_native_styling=False` to exclude an individual widget, or `adopt_native_widgets(page)` for a one-time scoped migration.

See the [existing-project migration guide](./migration.md) for mappings, semantic overrides, cleanup, and legacy QSS integration.

## Global configuration

Call `configure()` once near application startup. All later parameterless `apply_theme()` calls use this configuration.

```python
from shadcn_qt import configure, apply_theme

configure(
    theme="light",
    colors={"primary": "#7c3aed", "ring": "#8b5cf6"},
    radius={"sm": "6px", "md": "10px"},
    font={"sansFamily": "Inter, 'Segoe UI', sans-serif"},
    extra_qss="QWidget#sidebar { border-right: 1px solid #ddd; }",
)
apply_theme()
```

## Reusable custom themes

```python
from shadcn_qt import create_theme, register_theme, apply_theme

ocean = create_theme(
    "ocean",
    base="dark",
    colors={
        "primary": "#38bdf8",
        "primaryForeground": "#082f49",
        "ring": "#7dd3fc",
    },
)
register_theme(ocean)
apply_theme("ocean")
```

`create_theme()` merges the override into a complete light or dark base, so all semantic tokens remain defined.

## JSON theme

```json
{
  "name": "brand",
  "base": "light",
  "colors": {
    "primary": "#7c3aed",
    "ring": "#8b5cf6"
  },
  "radius": { "md": "10px" }
}
```

```python
from shadcn_qt import load_theme, apply_theme
apply_theme(load_theme("brand.json"))
```

## Token source and code generation

The repository's built-in palette lives in `packages/design-tokens/tokens.json`. After editing it, run:

```bash
python tools/token-codegen/generate.py
```

This writes Python QSS, the C++ resource QSS, and the C++ token header from the same source. Application-specific themes do not require regeneration; they are rendered at runtime.
