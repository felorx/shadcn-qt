import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="module")
def runtime():
    try:
        from shadcn_qt._qt import QtWidgets
    except ImportError as exc:
        pytest.skip(str(exc))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app, QtWidgets


def test_adopt_native_widgets_preserves_explicit_choices(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import Button, adopt_native_widgets

    root = QtWidgets.QWidget()
    button = QtWidgets.QPushButton("Save", root)
    button.setProperty("variant", "outline")
    line_edit = QtWidgets.QLineEdit(root)
    checkbox = QtWidgets.QCheckBox(root)
    opted_out = QtWidgets.QPushButton("Native", root)
    opted_out.setProperty("shadcn_qt_native_styling", False)
    custom = Button("Already shadcn-qt", root)

    combo = QtWidgets.QComboBox(root)
    combo.setEditable(True)
    internal_line_edit = combo.lineEdit()

    adopted = adopt_native_widgets(root)

    assert adopted >= 4
    assert button.property("shadcn_qt_component") == "button"
    assert button.property("variant") == "outline"
    assert button.property("shadcnSize") == "default"
    assert line_edit.property("shadcn_qt_component") == "input"
    assert checkbox.property("shadcn_qt_component") == "checkbox"
    assert combo.property("shadcn_qt_component") == "select"
    assert internal_line_edit.property("shadcn_qt_component") is None
    assert opted_out.property("shadcn_qt_component") is None
    assert custom.property("shadcn_qt_native_adopted") is None
    root.show()
    app.processEvents()
    assert not checkbox.grab().isNull()
    assert checkbox._shadcn_qt_native_enhancements.get("event_filter") is not None
    assert len(combo._shadcn_qt_native_enhancements.get("glyphs", ())) == 1
    assert line_edit.graphicsEffect().blurRadius() == 2.0
    assert line_edit.graphicsEffect().color().alpha() == 13
    assert button.graphicsEffect().blurRadius() == 4.0
    assert button.graphicsEffect().color().alpha() == 16

    # Clear markers added by the scoped operation before the global test.
    from shadcn_qt import disable_native_widget_styling

    assert disable_native_widget_styling(app, clear=True) >= adopted


def test_global_adapter_handles_future_widgets_and_opt_out(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import (
        disable_native_widget_styling,
        enable_native_widget_styling,
    )

    disable_native_widget_styling(app, clear=True)
    existing = QtWidgets.QPushButton("Existing")
    adapter = enable_native_widget_styling(app)
    assert adapter is enable_native_widget_styling(app)
    assert existing.property("shadcn_qt_component") == "button"
    assert app.property("shadcn_qt_native_styling_enabled") is True

    future = QtWidgets.QPushButton("Future")
    future.ensurePolished()
    app.processEvents()
    assert future.property("shadcn_qt_component") == "button"
    assert future.property("variant") == "default"
    assert future.property("shadcnSize") == "default"

    future.setProperty("shadcn_qt_native_styling", False)
    assert future.property("shadcn_qt_component") is None
    assert future.property("variant") is None

    future.setProperty("shadcn_qt_native_styling", True)
    assert future.property("shadcn_qt_component") == "button"
    future.setProperty("variant", "ghost")
    assert future.graphicsEffect() is None
    future.setProperty("variant", "destructive")
    assert future.graphicsEffect() is not None

    cleared = disable_native_widget_styling(app, clear=True)
    assert cleared >= 2
    assert existing.property("shadcn_qt_component") is None
    assert future.property("shadcn_qt_component") is None
    # User changes made after adoption are not deleted during cleanup.
    assert future.property("variant") == "destructive"
    assert app.property("shadcn_qt_native_styling_enabled") is False

    after_disable = QtWidgets.QPushButton("After disable")
    after_disable.ensurePolished()
    app.processEvents()
    assert after_disable.property("shadcn_qt_component") is None


def test_native_qt_widget_families_are_covered(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import (
        disable_native_widget_styling,
        enable_native_widget_styling,
    )
    from shadcn_qt._qt import QtCore

    disable_native_widget_styling(app, clear=True)
    root = QtWidgets.QWidget()
    horizontal = getattr(QtCore.Qt, "Horizontal", None)
    if horizontal is None:
        horizontal = QtCore.Qt.Orientation.Horizontal

    class ThirdPartyWidget(QtWidgets.QWidget):
        pass

    representatives = (
        (root, "widget"),
        (ThirdPartyWidget(root), "widget"),
        (QtWidgets.QFrame(root), "frame"),
        (QtWidgets.QLabel(root), "label"),
        (QtWidgets.QPushButton(root), "button"),
        (QtWidgets.QCommandLinkButton(root), "button"),
        (QtWidgets.QToolButton(root), "tool-button"),
        (QtWidgets.QCheckBox(root), "checkbox"),
        (QtWidgets.QRadioButton(root), "radio"),
        (QtWidgets.QLineEdit(root), "input"),
        (QtWidgets.QPlainTextEdit(root), "textarea"),
        (QtWidgets.QTextEdit(root), "text-edit"),
        (QtWidgets.QTextBrowser(root), "text-edit"),
        (QtWidgets.QKeySequenceEdit(root), "key-sequence-edit"),
        (QtWidgets.QSpinBox(root), "spin-box"),
        (QtWidgets.QDoubleSpinBox(root), "spin-box"),
        (QtWidgets.QDateEdit(root), "date-picker"),
        (QtWidgets.QTimeEdit(root), "date-picker"),
        (QtWidgets.QDateTimeEdit(root), "date-picker"),
        (QtWidgets.QComboBox(root), "select"),
        (QtWidgets.QFontComboBox(root), "select"),
        (QtWidgets.QSlider(root), "slider"),
        (QtWidgets.QDial(root), "dial"),
        (QtWidgets.QScrollBar(root), "scrollbar"),
        (QtWidgets.QProgressBar(root), "progress"),
        (QtWidgets.QTabWidget(root), "tabs"),
        (QtWidgets.QTabBar(root), "tab-bar"),
        (QtWidgets.QToolBox(root), "toolbox"),
        (QtWidgets.QStackedWidget(root), "stacked-widget"),
        (QtWidgets.QListView(root), "list-view"),
        (QtWidgets.QListWidget(root), "list-view"),
        (QtWidgets.QTreeView(root), "tree-view"),
        (QtWidgets.QTreeWidget(root), "tree-view"),
        (QtWidgets.QTableView(root), "data-table"),
        (QtWidgets.QTableWidget(root), "table"),
        (QtWidgets.QColumnView(root), "column-view"),
        (QtWidgets.QHeaderView(horizontal, root), "header-view"),
        (QtWidgets.QCalendarWidget(root), "calendar"),
        (QtWidgets.QScrollArea(root), "scroll-area"),
        (QtWidgets.QGraphicsView(root), "graphics-view"),
        (QtWidgets.QMdiArea(root), "mdi-area"),
        (QtWidgets.QMdiSubWindow(root), "mdi-subwindow"),
        (QtWidgets.QMenuBar(root), "menubar"),
        (QtWidgets.QMenu(root), "menu"),
        (QtWidgets.QToolBar(root), "toolbar"),
        (QtWidgets.QStatusBar(root), "statusbar"),
        (QtWidgets.QDockWidget(root), "dock-widget"),
        (QtWidgets.QGroupBox(root), "group-box"),
        (QtWidgets.QDialogButtonBox(root), "dialog-button-box"),
        (QtWidgets.QSplitter(root), "resizable"),
        (QtWidgets.QLCDNumber(root), "lcd-number"),
        (QtWidgets.QFocusFrame(root), "focus-frame"),
        (QtWidgets.QSizeGrip(root), "size-grip"),
        (QtWidgets.QDialog(root), "native-dialog"),
        (QtWidgets.QMainWindow(root), "main-window"),
        (QtWidgets.QWizard(root), "native-dialog"),
        (QtWidgets.QWizardPage(root), "wizard-page"),
    )

    enable_native_widget_styling(app)
    for widget, expected in representatives:
        assert widget.property("shadcn_qt_component") == expected, type(widget).__name__

    disable_native_widget_styling(app, clear=True)


def test_native_widget_runtime_enhancements_are_reversible(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import (
        apply_theme,
        disable_native_widget_styling,
        enable_native_widget_styling,
    )

    disable_native_widget_styling(app, clear=True)
    apply_theme(app, "light")
    root = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(root)
    checkbox = QtWidgets.QCheckBox("Checked", root)
    checkbox.setChecked(True)
    radio = QtWidgets.QRadioButton("Selected", root)
    radio.setChecked(True)
    calendar = QtWidgets.QCalendarWidget(root)
    original_delegate = calendar.findChild(
        QtWidgets.QTableView, "qt_calendar_calendarview"
    ).itemDelegate()
    separator = QtWidgets.QFrame(root)
    hline = getattr(QtWidgets.QFrame, "HLine", None)
    if hline is None:
        hline = QtWidgets.QFrame.Shape.HLine
    separator.setFrameShape(hline)
    buttons = QtWidgets.QDialogButtonBox(
        _standard_buttons(QtWidgets, "Cancel", "Save"), root
    )
    for widget in (checkbox, radio, calendar, separator, buttons):
        layout.addWidget(widget)

    enable_native_widget_styling(app)
    root.show()
    app.processEvents()

    view = calendar.findChild(QtWidgets.QTableView, "qt_calendar_calendarview")
    assert checkbox.property("nativeKind") == "check-box"
    assert radio.property("nativeKind") == "radio-button"
    assert separator.property("shadcn_qt_component") == "native-separator"
    assert separator.property("nativeKind") == "hline"
    assert type(view.itemDelegate()).__name__ == "NativeCalendarDelegate"
    assert view.verticalHeader().defaultSectionSize() == 36
    assert not checkbox.grab().isNull()
    assert not radio.grab().isNull()
    checkbox_image = checkbox.grab().toImage()
    radio_image = radio.grab().toImage()
    center_y = checkbox_image.height() // 2
    assert checkbox_image.pixelColor(0, center_y) != checkbox_image.pixelColor(
        3, center_y
    )
    assert radio_image.pixelColor(0, center_y) != radio_image.pixelColor(3, center_y)

    save = buttons.button(_standard_button(QtWidgets, "Save"))
    cancel = buttons.button(_standard_button(QtWidgets, "Cancel"))
    assert save.property("variant") == "default"
    assert cancel.property("variant") == "outline"

    disable_native_widget_styling(app, clear=True)
    assert calendar.property("shadcn_qt_component") is None
    assert type(view.itemDelegate()) is type(original_delegate)
    assert checkbox.property("shadcn_qt_component") is None
    root.close()


def test_native_stylesheet_has_dedicated_family_rules(runtime):
    from shadcn_qt import theme_stylesheet

    qss = theme_stylesheet("light")
    for selector in (
        'QWidget[shadcn_qt_native_adopted="true"]',
        'QToolBox[shadcn_qt_component="toolbox"]',
        'QStackedWidget[shadcn_qt_component="stacked-widget"]',
        'QGroupBox[shadcn_qt_component="group-box"]',
        'QGraphicsView[shadcn_qt_component="graphics-view"]',
        'QDialogButtonBox[shadcn_qt_component="dialog-button-box"]',
        'QFrame[shadcn_qt_component="native-separator"]',
        'QDialog[shadcn_qt_component="native-dialog"]',
    ):
        assert selector in qss
    assert 'QAbstractItemView[shadcn_qt_native_adopted="true"]::item:selected' in qss
    assert 'QAbstractItemView[shadcn_qt_native_adopted="true"]::item:selected:hover' in qss
    assert "QTableView::item:hover:!selected" in qss
    selected_rule = qss.split(
        'QAbstractItemView[shadcn_qt_native_adopted="true"]::item:selected:hover',
        1,
    )[1].split("}", 1)[0]
    assert "background: #f4f4f5" in selected_rule
    assert "color: #18181b" in selected_rule


def _standard_button(QtWidgets, name):
    value = getattr(QtWidgets.QDialogButtonBox, name, None)
    if value is not None:
        return value
    return getattr(QtWidgets.QDialogButtonBox.StandardButton, name)


def _standard_buttons(QtWidgets, *names):
    result = None
    for name in names:
        value = _standard_button(QtWidgets, name)
        result = value if result is None else result | value
    return result
