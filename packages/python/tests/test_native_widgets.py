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
    from shadcn_qt._qt import QtCore
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
    spin = QtWidgets.QSpinBox(root)

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
    combo_glyphs = combo._shadcn_qt_native_enhancements.get("glyphs", ())
    assert [glyph.direction for glyph in combo_glyphs] == ["down"]
    combo_glyph = combo_glyphs[0]
    combo_icon_bounds = combo_glyph._icon_path().boundingRect()
    assert (combo_icon_bounds.width(), combo_icon_bounds.height()) == (8.0, 4.0)
    assert combo_icon_bounds.center() == QtCore.QRectF(combo_glyph.rect()).center()
    assert combo_glyph.geometry().top() == 2
    assert combo_glyph.geometry().right() <= combo.rect().right() - 2
    assert combo_glyph.geometry().bottom() == combo.rect().bottom() - 2
    spin_glyphs = spin._shadcn_qt_native_enhancements.get("glyphs", ())
    assert [glyph.direction for glyph in spin_glyphs] == ["up", "down"]
    for glyph in spin_glyphs:
        icon_bounds = glyph._icon_path().boundingRect()
        assert (icon_bounds.width(), icon_bounds.height()) == (8.0, 4.0)
        assert icon_bounds.center() == QtCore.QRectF(glyph.rect()).center()
        assert glyph.geometry().right() <= spin.rect().right() - 2
    assert spin_glyphs[0].geometry().top() == 2
    assert spin_glyphs[-1].geometry().bottom() == spin.rect().bottom() - 2
    assert line_edit.graphicsEffect().blurRadius() == 2.0
    assert line_edit.graphicsEffect().color().alpha() == 13
    assert button.graphicsEffect().blurRadius() == 4.0
    assert button.graphicsEffect().color().alpha() == 16

    # Clear markers added by the scoped operation before the global test.
    from shadcn_qt import disable_native_widget_styling

    assert disable_native_widget_styling(app, clear=True) >= adopted


def test_native_combo_popup_has_one_outer_border(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import (
        adopt_native_widgets,
        apply_theme,
        disable_native_widget_styling,
    )
    from shadcn_qt._qt import QtCore, import_qt_module

    QtTest = import_qt_module("QtTest")

    disable_native_widget_styling(app, clear=True)
    apply_theme(app, "light")
    combo = QtWidgets.QComboBox()
    combo.addItems(["PySide6", "PyQt6", "PySide2", "PyQt5"])
    combo.resize(300, 36)
    view = combo.view()
    popup = view.window()
    original_popup_name = popup.objectName()
    original_popup_stylesheet = popup.styleSheet()
    original_popup_minimum_width = popup.minimumWidth()
    original_popup_maximum_width = popup.maximumWidth()
    original_view_name = view.objectName()

    assert adopt_native_widgets(combo) >= 1
    assert popup.objectName() == "shadcnQtNativeComboPopup"
    assert view.objectName() == "shadcnQtNativeComboPopupView"
    assert view.property("shadcn_qt_native_adopted") is None
    assert popup.styleSheet().count("border: 1px solid") == 1
    assert "QListView { background: transparent" in popup.styleSheet()
    assert "border: none" in popup.styleSheet()

    combo.show()
    app.processEvents()
    left_button = getattr(QtCore.Qt, "LeftButton", None)
    if left_button is None:
        left_button = QtCore.Qt.MouseButton.LeftButton
    trigger_point = combo.rect().center()
    QtTest.QTest.mousePress(combo, left_button, pos=trigger_point)
    app.processEvents()
    assert not view.isVisible()
    QtTest.QTest.mouseRelease(combo, left_button, pos=trigger_point)
    app.processEvents()
    assert view.isVisible()
    expected_popup_position = combo.mapToGlobal(QtCore.QPoint(0, combo.height()))
    assert popup.pos() == expected_popup_position
    assert popup.width() == combo.width()
    assert view.frameWidth() == 4
    image = popup.grab().toImage()
    center_x = image.width() // 2
    assert image.pixelColor(center_x, 0) != image.pixelColor(center_x, 1)
    assert image.pixelColor(center_x, 1) == image.pixelColor(center_x, 2)
    assert image.pixelColor(center_x, image.height() - 1) != image.pixelColor(
        center_x, image.height() - 2
    )
    assert image.pixelColor(
        center_x, image.height() - 2
    ) == image.pixelColor(center_x, image.height() - 3)

    apply_theme(app, "dark")
    app.processEvents()
    assert "background: #09090b" in popup.styleSheet()
    assert "border: 1px solid #27272a" in popup.styleSheet()

    combo.hidePopup()
    assert disable_native_widget_styling(app, clear=True) >= 1
    assert popup.objectName() == original_popup_name
    assert popup.styleSheet() == original_popup_stylesheet
    assert popup.minimumWidth() == original_popup_minimum_width
    assert popup.maximumWidth() == original_popup_maximum_width
    assert view.objectName() == original_view_name
    combo.close()


def test_native_date_popup_is_left_aligned_directly_below(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import (
        disable_native_widget_styling,
        enable_native_widget_styling,
    )
    from shadcn_qt._qt import QtCore, import_qt_module

    QtTest = import_qt_module("QtTest")
    disable_native_widget_styling(app, clear=True)
    enable_native_widget_styling(app)
    date = QtWidgets.QDateEdit()
    date.setCalendarPopup(True)
    date.resize(300, 36)
    date.show()
    app.processEvents()

    left_button = getattr(QtCore.Qt, "LeftButton", None)
    if left_button is None:
        left_button = QtCore.Qt.MouseButton.LeftButton
    QtTest.QTest.mouseClick(
        date,
        left_button,
        pos=QtCore.QPoint(date.width() - 16, date.height() // 2),
    )
    app.processEvents()

    popup = date.calendarWidget().window()
    expected_popup_position = date.mapToGlobal(QtCore.QPoint(0, date.height()))
    assert popup.isVisible()
    assert popup.pos() == expected_popup_position

    popup.hide()
    disable_native_widget_styling(app, clear=True)
    date.close()


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


def test_future_font_combo_restores_runtime_enhancements(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import disable_native_widget_styling, enable_native_widget_styling
    from shadcn_qt._qt import QtCore

    disable_native_widget_styling(app, clear=True)
    enable_native_widget_styling(app)
    combo = QtWidgets.QFontComboBox()
    combo.resize(300, 36)
    combo.show()
    app.processEvents()

    state = combo._shadcn_qt_native_enhancements
    assert combo.property("shadcn_qt_component") == "select"
    assert [glyph.direction for glyph in state["glyphs"]] == ["down"]
    assert state["glyphs"][0].isVisible()
    assert state.get("combo_popup") is not None

    combo.showPopup()
    app.processEvents()
    popup = combo.view().window()
    expected_popup_position = combo.mapToGlobal(QtCore.QPoint(0, combo.height()))
    assert popup.pos() == expected_popup_position
    combo.hidePopup()

    disable_native_widget_styling(app, clear=True)
    combo.close()


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
        (QtWidgets.QTabWidget(root), "tab-pane"),
        (QtWidgets.QTabBar(root), "tab-pane-bar"),
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


def test_native_tab_widget_keeps_behavior_and_owns_its_chrome_bar(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import adopt_native_widgets, disable_native_widget_styling

    disable_native_widget_styling(app, clear=True)
    pane = QtWidgets.QTabWidget()
    pane.setMovable(True)
    pane.setTabsClosable(True)
    original_elide_mode = pane.tabBar().elideMode()
    pane.tabBar().setMouseTracking(False)
    pane.tabBar().setUsesScrollButtons(False)
    pane.addTab(QtWidgets.QWidget(pane), "First")
    pane.addTab(QtWidgets.QWidget(pane), "Second")

    adopt_native_widgets(pane)
    pane.resize(420, 180)
    pane.show()
    app.processEvents()

    assert pane.property("shadcn_qt_component") == "tab-pane"
    assert pane.property("nativeKind") == "tab-widget"
    assert pane.isMovable()
    assert pane.tabsClosable()
    assert pane.count() == 2
    assert pane.tabBar().property("shadcn_qt_native_adopted") is None
    assert pane.findChild(QtWidgets.QStackedWidget).property(
        "shadcn_qt_native_adopted"
    ) is None
    close_buttons = [
        button
        for button in pane.tabBar().findChildren(QtWidgets.QAbstractButton)
        if button.property("tabPaneCloseButton") is True
    ]
    assert len(close_buttons) == 2

    disable_native_widget_styling(app, clear=True)
    app.processEvents()
    assert pane.property("shadcn_qt_component") is None
    assert pane.isMovable()
    assert pane.tabsClosable()
    assert pane.tabBar().elideMode() == original_elide_mode
    assert not pane.tabBar().hasMouseTracking()
    assert not pane.tabBar().usesScrollButtons()
    right = getattr(QtWidgets.QTabBar, "RightSide", None)
    left = getattr(QtWidgets.QTabBar, "LeftSide", None)
    if right is None:
        right = QtWidgets.QTabBar.ButtonPosition.RightSide
        left = QtWidgets.QTabBar.ButtonPosition.LeftSide
    active_buttons = [
        pane.tabBar().tabButton(index, position)
        for index in range(pane.count())
        for position in (right, left)
    ]
    assert not any(
        button is not None and button.property("tabPaneCloseButton") is True
        for button in active_buttons
    )
    pane.close()


@pytest.mark.parametrize(
    ("theme_name", "surface_color"),
    (("light", "#fafafa"), ("dark", "#18181a")),
)
def test_native_tab_widget_initial_page_matches_active_tab_surface(
    runtime, theme_name, surface_color
):
    app, QtWidgets = runtime
    from shadcn_qt import (
        apply_theme,
        disable_native_widget_styling,
        enable_native_widget_styling,
    )

    disable_native_widget_styling(app, clear=True)
    apply_theme(app, theme_name)
    enable_native_widget_styling(app)
    pane = QtWidgets.QTabWidget()
    pane.resize(420, 180)
    pane.addTab(QtWidgets.QWidget(pane), "Account")
    pane.addTab(QtWidgets.QWidget(pane), "Security")
    pane.show()
    app.processEvents()

    assert pane.widget(0).property("shadcn_qt_native_adopted") is None
    image = pane.grab().toImage()
    ratio = image.devicePixelRatio()

    def pixel_color(x, y):
        return image.pixelColor(round(x * ratio), round(y * ratio)).name()

    tab_rect = pane.tabBar().tabRect(0)
    title_color = pixel_color(tab_rect.left() + 20, tab_rect.center().y())
    page_color = pixel_color(pane.width() // 2, pane.height() // 2)
    assert title_color == surface_color
    assert page_color == title_color

    pane.close()
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
    assert "margin: 2px; border-radius: 4px" in qss
    assert "margin: 2px 2px 0 0; border-radius: 4px" in qss
    assert "margin: 0 2px 2px 0; border-radius: 4px" in qss
    selected_rule = qss.split(
        'QAbstractItemView[shadcn_qt_native_adopted="true"]::item:selected:hover',
        1,
    )[1].split("}", 1)[0]
    assert "background: #f4f4f5" in selected_rule
    assert "color: #18181b" in selected_rule


def test_native_group_box_title_and_default_content_are_left_aligned(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import (
        apply_theme,
        disable_native_widget_styling,
        enable_native_widget_styling,
    )

    disable_native_widget_styling(app, clear=True)
    apply_theme(app, "light")
    enable_native_widget_styling(app)
    group = QtWidgets.QGroupBox("Account settings")
    layout = QtWidgets.QVBoxLayout(group)
    editor = QtWidgets.QLineEdit(group)
    layout.addWidget(editor)
    group.resize(420, 120)
    group.show()
    app.processEvents()

    option = QtWidgets.QStyleOptionGroupBox()
    group.initStyleOption(option)
    style = QtWidgets.QStyle
    complex_control = getattr(style, "CC_GroupBox", None)
    label_control = getattr(style, "SC_GroupBoxLabel", None)
    if complex_control is None:
        complex_control = style.ComplexControl.CC_GroupBox
        label_control = style.SubControl.SC_GroupBoxLabel
    title_rect = group.style().subControlRect(
        complex_control,
        option,
        label_control,
        group,
    )
    assert group.contentsRect().left() <= 2
    assert editor.geometry().left() == title_rect.left()

    group.close()
    disable_native_widget_styling(app, clear=True)


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
