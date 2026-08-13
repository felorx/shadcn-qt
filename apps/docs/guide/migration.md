# Migrate an existing Qt project

An existing PySide or PyQt application does not need to be rewritten to adopt
shadcn-qt. The safest path is incremental:

1. keep the current Qt binding and application structure;
2. introduce the theme at one controlled entry point;
3. migrate simple widgets page by page;
4. use compound components for new or redesigned screens.

## Install without replacing Qt

If the project already has PySide or PyQt installed, install shadcn-qt without a binding extra. The base package has no Qt dependency and therefore does not upgrade or replace the project's existing binding.

From PyPI:

```bash
python -m pip install shadcn-qt
```

Use an optional extra only when creating a new environment that does not already contain Qt:

```bash
python -m pip install "shadcn-qt[pyside6]"
```

## Select exactly one Qt binding

Set `SHADCN_QT_BINDING` before the first import from `shadcn_qt`. This is especially important when more than one Qt binding is installed in the environment.

```python
import os

os.environ.setdefault("SHADCN_QT_BINDING", "PyQt5")

from PyQt5.QtWidgets import QApplication
from shadcn_qt import apply_theme
```

Valid values are `PySide6`, `PyQt6`, `PySide2`, and `PyQt5`. Do not import widgets from two different bindings in the same process.

For deployed applications, the same setting can be supplied by the launcher instead of application code:

```bash
SHADCN_QT_BINDING=PyQt5 python main.py
```

## Level 1: add the theme without replacing widgets

Create the existing `QApplication` as usual, then apply the theme once at application startup:

```python
import os

os.environ.setdefault("SHADCN_QT_BINDING", "PyQt5")

from PyQt5.QtWidgets import QApplication
from shadcn_qt import apply_theme, configure

app = QApplication([])

configure(
    theme="light",
    colors={"primary": "#2563eb", "ring": "#3b82f6"},
    radius={"sm": "4px", "md": "8px"},
)
apply_theme(app)
```

This immediately supplies the global palette, window colors, menus, tooltips, table headers, and shared tokens. Enable native-widget styling for full default component styling without replacing widget classes.

If the application relies heavily on its existing `QPalette`, begin with palette changes disabled:

```python
apply_theme(app, "light", apply_palette=False)
```

## Level 2: automatically style native widgets

Compatibility mode applies shadcn-qt's complete default component properties to existing standard Qt widgets. It also watches widgets created later, so dialogs and pages constructed on demand receive the same styling.

Enable it after creating `QApplication`; enabling it before constructing windows avoids an extra repolish pass:

```python
from shadcn_qt import apply_theme, enable_native_widget_styling

app = QApplication([])
enable_native_widget_styling(app)

window = MainWindow()
apply_theme(app, "light")
window.show()
```

Calling it after windows already exist is also supported. Existing widgets are scanned immediately:

```python
window = MainWindow()
enable_native_widget_styling(app)
apply_theme(app, "light")
```

The adapter covers the complete `QtWidgets` QWidget family. Known controls receive component-specific styling; containers and uncommon/third-party QWidget subclasses receive a neutral themed fallback so they do not retain an unrelated platform appearance.

The adapter also supplies reversible behavior for details QSS cannot render
faithfully: checkbox/radio glyphs use antialiased Qt painting, calendar day
cells use a compact delegate, ComboBox and SpinBox arrows use theme-aware
overlay glyphs, and common input/action surfaces receive subtle new-york
elevation. Disabling compatibility mode removes these enhancements together
with unchanged adapter properties.

| Native family | Automatic styling |
|---|---|
| Buttons | `QPushButton`, `QCommandLinkButton`, `QToolButton`, `QCheckBox`, `QRadioButton`, dialog buttons |
| Text and value editors | `QLineEdit`, `QPlainTextEdit`, `QTextEdit`, `QTextBrowser`, `QKeySequenceEdit`, all SpinBox and date/time editors |
| Selection controls | `QComboBox`, `QFontComboBox`, `QSlider`, `QDial`, `QScrollBar` |
| Data and progress | `QProgressBar`, `QLCDNumber`, `QCalendarWidget` |
| Item views | Table, Tree, List, Column, Header, Widget, and Undo view variants |
| Containers | `QTabWidget`, `QTabBar`, `QToolBox`, `QStackedWidget`, `QGroupBox`, `QSplitter`, scroll areas, graphics views, and MDI widgets |
| Window chrome | `QMenu`, `QMenuBar`, `QToolBar`, `QStatusBar`, `QDockWidget`, and dialog button boxes |
| Windows and dialogs | `QMainWindow`, `QDialog`, message/file/color/font/input/progress dialogs, Wizard and WizardPage |
| Miscellaneous | `QFrame`, `QFocusFrame`, `QSizeGrip`, `QRubberBand`, splash/RHI/custom widgets, and any remaining `QWidget` subclass |

Embedded `QLineEdit` instances owned by ComboBox and SpinBox controls are styled through their parent to avoid double borders. Existing explicit `shadcn_qt_component` values and shadcn-qt subclasses are preserved. Calling the enable function more than once returns the already installed adapter.

Compatibility mode covers Qt Widgets. Qt Quick/QML scenes, web-page content, video frames, OpenGL/RHI drawing surfaces, and third-party controls that completely replace `paintEvent()` cannot be restyled internally by QSS; their surrounding QWidget chrome still receives the neutral fallback. Theme those rendering systems through their own APIs, or opt custom-painted widgets out when appropriate.

Operating-system-native file, color, and font dialogs may intentionally ignore
Qt widget styling. Request Qt's non-native dialog implementation when a fully
themed dialog surface is required. MDI title bars and other platform-owned
window decorations may also vary by platform while their content and frame
tokens remain themed.

### Override semantics without changing classes

The widget type determines only a safe default. Set dynamic properties when application semantics require a different component or variant:

```python
delete_button.setProperty("variant", "destructive")
secondary_button.setProperty("variant", "outline")
notifications_checkbox.setProperty("shadcn_qt_component", "switch")
status_label.setProperty("shadcn_qt_component", "badge")
status_label.setProperty("variant", "secondary")
```

Property changes on adopted widgets trigger a style refresh automatically.

Ambiguous classes receive a neutral default: `QFrame` becomes a themed frame, `QToolButton` a standard tool button, and unknown QWidget subclasses use the base background/foreground. Mark Card, Alert, Sidebar, Toggle, Switch, Badge, and similar application semantics explicitly when the neutral default is not specific enough.

### Opt out one widget

Set the preference before or after enabling compatibility mode:

```python
custom_control.setProperty("shadcn_qt_native_styling", False)
```

Setting it to `False` after adoption removes unchanged defaults immediately. Set it to `True` to adopt the widget again.

### Adopt only one window or page

For a scoped migration without a global event filter:

```python
from shadcn_qt import adopt_native_widgets, theme_stylesheet

adopt_native_widgets(settings_page)
settings_page.setStyleSheet(theme_stylesheet("light"))
```

`adopt_native_widgets()` returns the number of newly adopted widgets. It accepts either a `QWidget` or `QApplication` root.

### Disable compatibility mode

```python
from shadcn_qt import disable_native_widget_styling

disable_native_widget_styling(app)
```

By default this stops future adoption and removes adapter-added properties that the application has not changed. User overrides are preserved. Use `clear=False` to stop watching while keeping current styling properties:

```python
disable_native_widget_styling(app, clear=False)
```

### Try one page first

To limit the first trial to one page or panel, set the generated stylesheet on that widget rather than on `QApplication`:

```python
from shadcn_qt import theme_stylesheet

settings_page.setStyleSheet(theme_stylesheet("light"))
```

Widget stylesheets cascade to descendants, while the rest of the application remains unchanged. This scoped approach does not modify the application palette.

## Preserve existing QSS

Pass the legacy stylesheet through `extra_qss`. It is appended after shadcn-qt's generated rules, so existing object-name selectors and deliberate overrides win.

```python
from pathlib import Path

from shadcn_qt import apply_theme, configure

legacy_qss = Path("resources/legacy.qss").read_text(encoding="utf-8")

configure(
    theme="light",
    extra_qss=legacy_qss,
)
apply_theme(app)
```

Do not call `app.setStyleSheet(legacy_qss)` after `apply_theme()`: that would replace the generated theme. Either use `extra_qss` or concatenate the additional rules before making the final `setStyleSheet()` call.

For a temporary page-level trial:

```python
settings_page.setStyleSheet(
    theme_stylesheet("light", extra_qss=legacy_qss)
)
```

## Level 3: migrate simple widgets gradually

shadcn-qt primitives subclass standard Qt widgets, so their inherited signals, slots, methods, models, and accessibility properties remain available.

| Existing Qt widget | shadcn-qt replacement | Notes |
|---|---|---|
| `QPushButton` | `Button` | Adds `variant` and `shadcnSize` |
| `QLineEdit` | `Input` | Adds the `invalid` state |
| `QPlainTextEdit` | `TextArea` | Adds the `invalid` state |
| `QFrame` | `Card`, `Alert`, `Separator` | Select according to semantics |
| `QLabel` | `Label`, `Badge`, `Typography` | Adds semantic text presets |
| `QCheckBox` | `Checkbox`, `Switch` | Both retain `toggled` and `stateChanged` |
| `QRadioButton` | `RadioButton` | Use `RadioGroup` for composed forms |
| `QComboBox` | `Select`, `NativeSelect`, `Combobox` | `Combobox` is editable |
| `QSlider` | `Slider` | Retains range/value APIs |
| `QProgressBar` | `Progress`, `Spinner` | Spinner uses an indeterminate range |
| `QTabWidget` | `Tabs` | Retains the normal tab API |
| `QTableWidget` | `Table` | Native item-based table |
| `QTableView` | `DataTable` | Includes source/proxy model helpers |
| `QCalendarWidget` | `Calendar` | Native calendar behavior |

Before:

```python
from PyQt5.QtWidgets import QLineEdit, QPushButton

name_input = QLineEdit()
save_button = QPushButton("Save")
save_button.clicked.connect(save_record)
```

After:

```python
from shadcn_qt import Button, Input

name_input = Input()
save_button = Button("Save", variant="default")
save_button.clicked.connect(save_record)
```

Migrate primitives independently. Compound components such as `Dialog`, `Accordion`, `Sidebar`, `Command`, and `DataTable` add structure and behavior, so adopt them as intentional page-level changes rather than global search-and-replace operations.

## Level 4: promote widgets in existing `.ui` files

Existing Qt Designer forms can be migrated without recreating their layouts:

1. open the old `.ui` file;
2. select a widget such as `QPushButton`;
3. choose **Promote to…** from the context menu;
4. enter `Button` as the promoted class name;
5. enter `shadcn_qt.widgets` as the header file;
6. choose **Add**, then **Promote**;
7. save the form.

Common promotions:

| Base class | Promoted class | Header |
|---|---|---|
| `QPushButton` | `Button` | `shadcn_qt.widgets` |
| `QLineEdit` | `Input` | `shadcn_qt.widgets` |
| `QPlainTextEdit` | `TextArea` | `shadcn_qt.widgets` |
| `QFrame` | `Card` | `shadcn_qt.widgets` |
| `QLabel` | `Label` | `shadcn_qt.widgets` |
| `QCheckBox` | `Switch` | `shadcn_qt.widgets` |
| `QTabWidget` | `Tabs` | `shadcn_qt.widgets` |

After promotion, properties such as `variant`, `shadcnSize`, `invalid`, and
`elevated` appear in the Property Editor. Use the `shadcn-qt` Widget Box group
for new compound components.

Load the saved form through the binding-independent loader:

```python
from shadcn_qt.designer import load_ui

window = load_ui("mainwindow.ui")
```

PyQt uses its native `uic.loadUi`; PySide uses `QUiLoader` with all shadcn-qt classes registered automatically. If the project generates Python files with `pyuic` or `pyside-uic`, regenerate those files after changing the `.ui` file.

## Keep Designer separate from a legacy runtime

The recommended Python custom-widget host is `pyside6-designer`. A PyQt5 or PySide2 production project can keep its runtime environment unchanged and use a separate Designer environment:

```bash
python3 -m venv .designer-venv
source .designer-venv/bin/activate

python -m pip install "shadcn-qt[designer]"
shadcn-qt-designer path/to/mainwindow.ui
```

The `.ui` format is binding-independent. A form saved by the PySide6 Designer host can still be loaded by a PyQt5, PyQt6, PySide2, or PySide6 application.

Do not import PySide6 Designer modules inside the PyQt/PySide runtime process. The separate environment exists only for editing forms.

## Theme switching and custom branding

Centralize theme switching so pages do not manipulate stylesheets independently:

```python
from shadcn_qt import apply_theme, configure

configure(
    colors={"primary": "#7c3aed", "ring": "#8b5cf6"},
    extra_qss=legacy_qss,
)


def set_theme(name: str) -> None:
    apply_theme(app, name)
```

Application-specific themes can also be stored as JSON and loaded at runtime:

```python
from shadcn_qt import apply_theme, load_theme

apply_theme(app, theme=load_theme("themes/brand.json"))
```

## Recommended rollout

1. add shadcn-qt to the existing environment without a Qt extra;
2. pin `SHADCN_QT_BINDING` at the application entry point;
3. merge the existing QSS through `extra_qss`;
4. enable native-widget styling globally, or adopt one low-risk page;
5. mark special semantics such as Switch, Badge, Card, and destructive Button;
6. migrate classes only where typed properties or compound APIs add value;
7. promote matching widgets in existing `.ui` files when desired;
8. use compound components for new screens;
9. remove obsolete legacy QSS only after visual and interaction checks pass;
10. move from page-level styling to `apply_theme(app)` when the application is ready.

## Migration checklist

- Only one PySide/PyQt binding is imported in the process.
- `SHADCN_QT_BINDING` is set before importing `shadcn_qt` widgets.
- `QApplication` exists before calling `apply_theme()`.
- Native compatibility mode is enabled before constructing most windows when possible.
- Ambiguous widgets such as Switch, Badge, and Card are marked explicitly.
- Third-party or custom-painted widgets opt out with `shadcn_qt_native_styling=False` when necessary.
- Legacy QSS is appended through `extra_qss`, not applied afterward.
- Promoted `.ui` classes use the header `shadcn_qt.widgets`.
- Generated Python UI files are regenerated after `.ui` changes.
- Light and dark themes are checked on at least one representative form.
- Keyboard focus, disabled states, validation states, tables, and popup menus are smoke-tested.
- The Designer host and legacy runtime use separate environments when their Qt bindings differ.

The migration remains reversible at every stage: unpromoted widgets continue to work, page-level styles can be removed independently, and compound components can be introduced without changing unrelated screens.
