# Native QtWidgets

shadcn-qt can apply the classic `new-york` + Zinc profile to an existing
QtWidgets application without replacing its widget classes. The compatibility
layer is opt-in, continuously adopts widgets created later, and is reversible.

```python
from shadcn_qt import (
    apply_theme,
    configure_high_dpi,
    enable_native_widget_styling,
)
from shadcn_qt._qt import QtWidgets

configure_high_dpi()
app = QtWidgets.QApplication([])
enable_native_widget_styling(app)
apply_theme(app, "light")
```

## Coverage

| Family | Examples | Adaptation |
|---|---|---|
| Actions | QPushButton, QCommandLinkButton, QToolButton, QDialogButtonBox | new-york geometry, semantic variants, states, elevation |
| Choices | QCheckBox, QRadioButton | antialiased check/radio glyphs, focus and disabled states |
| Editors | QLineEdit, QTextEdit, QKeySequenceEdit, SpinBox and date/time editors | input geometry, validation, focus, themed arrows |
| Selection | QComboBox, QFontComboBox, QSlider, QDial, QScrollBar | themed controls, tracks, handles, 32px-minimum popup options, arrows |
| Data | List, Tree, Table, Column, Header and Calendar widgets | selection hierarchy, headers, scrollbars, compact calendar delegate |
| Containers | Chrome-style TabPane/QTabWidget, ToolBox, StackedWidget, GroupBox, Splitter, ScrollArea, GraphicsView, MDI | document-tab states, borders, surfaces, disclosure states, handles |
| Window chrome | QMenuBar, QMenu, QToolBar, QStatusBar, QDockWidget | themed menus, actions, separators and dock controls |
| Dialogs | QDialog, QMessageBox, QFileDialog, QWizard and related classes | themed Qt-owned surfaces and child controls |
| Fallback | uncommon and third-party QWidget subclasses | neutral background and foreground tokens |

Every adopted widget receives `shadcn_qt_component` and `nativeKind` dynamic
properties. Existing explicit properties win, allowing semantic overrides
without subclassing.

## Reversible enhancements

Some official shapes cannot be expressed reliably in QSS. The adapter uses an
application event filter to paint checkbox/radio indicators and installs a
calendar delegate, themed editor arrows, and subtle elevation where needed.
Combo popups use a delegate proxy to enforce the 32px `new-york` row minimum,
including when a model or custom delegate requests a smaller size. Larger
business-defined rows and custom painting/editing behavior are preserved, and
delegates replaced after adoption are detected when the control or popup is
shown. `disable_native_widget_styling(app)` restores the current original combo
and calendar delegates, removes adapter glyphs/effects, and clears only
unchanged adapter defaults.

Set `shadcn_qt_native_styling=False` on custom-painted or third-party controls
that should remain untouched.

## Gallery and screenshot regression

The Gallery has a dedicated **Native QtWidgets** navigation group:

- Native Forms
- Native Data Views
- Native Containers
- Native Window Chrome

These pages use stock Qt classes rather than shadcn-qt component subclasses.
Open one directly:

```bash
python examples/python_gallery/run.py --component "Native Data Views" --theme dark
```

Eight light/dark screenshots are committed under
`packages/python/tests/baselines/native_gallery`. Regenerate and verify them:

```bash
python tools/update_native_gallery_baselines.py
pytest -q packages/python/tests/test_native_gallery_screenshots.py
```

The regression test uses downsampled perceptual comparison to tolerate minor
font rasterization differences while still catching layout, palette, missing
control, and large state regressions.

## Platform boundaries

OS-native file/color/font dialog implementations and platform window
decorations can remain under operating-system control. Select Qt's non-native
dialog implementation when the entire dialog must follow the theme. Qt
Quick/QML, web content, OpenGL/RHI scenes, and third-party controls that replace
painting require their own theming APIs.
