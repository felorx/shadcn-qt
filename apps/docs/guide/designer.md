# Qt Designer

qtshadcn ships a Python custom-widget registration catalog. In Designer, widgets appear in a **qtshadcn** group and can be dragged into forms, arranged with normal Qt layouts, and configured in the Property Editor.

## Launch

PySide6 provides the supported Python plugin host used by `pyside6-designer`. The qtshadcn launcher sets `PYSIDE_DESIGNER_PLUGINS`, `PYQTDESIGNERPATH`, and the binding selection before starting it.

```bash
pip install -e ".[designer]"
qtshadcn-designer
```

Diagnostics:

```bash
qtshadcn-designer --print-plugin-path
qtshadcn-designer --print-command
```

If Designer is in a nonstandard location, set `QTSHADCN_DESIGNER` to its executable.

Designer previews the light theme by default. Select dark mode or a custom JSON theme before launch:

```bash
QTSHADCN_DESIGNER_THEME=dark qtshadcn-designer
QTSHADCN_DESIGNER_THEME=./brand.json qtshadcn-designer
```

The preview stylesheet is scoped to qtshadcn components and does not restyle Designer itself. The application still chooses its runtime theme with `configure()` / `apply_theme()`.

## Editable custom properties

| Widget | Properties |
|---|---|
| Button | `variant`, `shadcnSize`, plus all QPushButton properties |
| Input / TextArea | `invalid`, plus inherited text properties |
| Card | `elevated` |
| Label / Badge / Alert | `variant` |
| Separator | `orientation` (`horizontal` or `vertical`) |
| Other widgets | Their normal Qt properties, such as `checked`, `value`, `items`, and `currentIndex` |

Card, Alert, and Tabs are registered as containers. Normal Qt layout tools remain responsible for margins, spacing, stretch, and alignment.

## Use the saved form

The same `.ui` file works with PySide and PyQt:

```python
from qtshadcn import apply_theme
from qtshadcn._qt import QtWidgets
from qtshadcn.designer import load_ui

app = QtWidgets.QApplication([])
apply_theme(app, "dark")
window = load_ui("mainwindow.ui")
window.show()
```

PyQt uses `uic.loadUi`; PySide uses `QUiLoader` with all qtshadcn classes registered automatically. A complete example is in `examples/python_designer`.

## Troubleshooting

- Launch through `qtshadcn-designer`; a standalone Designer that is ABI-incompatible with the selected Python binding cannot load Python plugins.
- Check **Help → About Plugins** for import errors.
- Ensure the environment used to launch Designer can import `qtshadcn`.
- Set `QTSHADCN_QT_BINDING=PySide6` (or the intended binding) before importing any Qt module.
