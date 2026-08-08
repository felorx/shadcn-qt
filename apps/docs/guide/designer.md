# Qt Designer

shadcn-qt ships a Python custom-widget registration catalog. In Designer,
widgets appear in a **shadcn-qt** group and can be dragged into forms,
arranged with normal Qt layouts, and configured in the Property Editor.

## Launch

PySide6 provides the supported Python plugin host used by `pyside6-designer`. The shadcn-qt launcher sets `PYSIDE_DESIGNER_PLUGINS`, `PYQTDESIGNERPATH`, and the binding selection before starting it.

```bash
pip install "shadcn-qt[designer]"
shadcn-qt-designer
```

Diagnostics:

```bash
shadcn-qt-designer --print-plugin-path
shadcn-qt-designer --print-command
```

If Designer is in a nonstandard location, set `SHADCN_QT_DESIGNER` to its executable.

Designer previews the light theme by default. Select dark mode or a custom JSON theme before launch:

```bash
SHADCN_QT_DESIGNER_THEME=dark shadcn-qt-designer
SHADCN_QT_DESIGNER_THEME=./brand.json shadcn-qt-designer
```

The preview stylesheet is scoped to shadcn-qt components and does not restyle Designer itself. The application still chooses its runtime theme with `configure()` / `apply_theme()`.

## Editable custom properties

| Widget | Properties |
|---|---|
| Button | `variant`, `shadcnSize`, plus all QPushButton properties |
| Input / TextArea | `invalid`, plus inherited text properties |
| Card | `elevated` |
| Label / Badge / Alert / Toggle / Bubble / Toast | `variant` |
| Separator | `orientation` (`horizontal` or `vertical`) |
| Accordion / Collapsible | `exclusive`, `title`, `expanded` |
| Sheet / Sidebar | `side`, `collapsed` |
| Direction | `direction` (`ltr` or `rtl`) |
| Chart | `chartType`, comma-separated `values` |
| Typography | `level` (`h1`–`h4`, `p`, `lead`, `code`, and other presets) |
| Pagination / InputOTP | `currentPage`, `pageCount`, `codeLength`, `value` |
| Other widgets | Their normal Qt properties, such as `checked`, `value`, `items`, and `currentIndex` |

Card, Alert, Tabs, AspectRatio, Direction, Resizable, ScrollArea, and Sidebar are registered as containers. Normal Qt layout tools remain responsible for margins, spacing, stretch, and alignment.

## Use the saved form

The same `.ui` file works with PySide and PyQt:

```python
from shadcn_qt import apply_theme
from shadcn_qt._qt import QtWidgets
from shadcn_qt.designer import load_ui

app = QtWidgets.QApplication([])
apply_theme(app, "dark")
window = load_ui("mainwindow.ui")
window.show()
```

PyQt uses `uic.loadUi`; PySide uses `QUiLoader` with all shadcn-qt classes registered automatically. A complete example is in `examples/python_designer`.

## Troubleshooting

- Launch through `shadcn-qt-designer`; a standalone Designer that is ABI-incompatible with the selected Python binding cannot load Python plugins.
- Check **Help → About Plugins** for import errors.
- Ensure the environment used to launch Designer can import `shadcn_qt`.
- Set `SHADCN_QT_BINDING=PySide6` (or the intended binding) before importing any Qt module.
