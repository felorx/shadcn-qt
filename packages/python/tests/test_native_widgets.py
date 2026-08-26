import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


def _assert_color_close(actual, expected, tolerance=6):
    actual_channels = tuple(
        int(actual[index : index + 2], 16) for index in (1, 3, 5)
    )
    expected_channels = tuple(
        int(expected[index : index + 2], 16) for index in (1, 3, 5)
    )
    assert max(
        abs(left - right)
        for left, right in zip(actual_channels, expected_channels)
    ) <= tolerance


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


def test_native_item_view_refresh_uses_qwidget_overload(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import adopt_native_widgets, disable_native_widget_styling

    disable_native_widget_styling(app, clear=True)
    view = QtWidgets.QListView()
    assert adopt_native_widgets(view) >= 1
    assert disable_native_widget_styling(app, clear=True) >= 1
    view.close()


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
    size_hint_role = getattr(QtCore.Qt, "SizeHintRole", None)
    if size_hint_role is None:
        size_hint_role = QtCore.Qt.ItemDataRole.SizeHintRole
    combo.setItemData(1, QtCore.QSize(80, 40), size_hint_role)
    combo.resize(300, 36)
    view = combo.view()

    class CompactLegacyDelegate(QtWidgets.QStyledItemDelegate):
        def sizeHint(self, option, index):
            hint = super().sizeHint(option, index)
            if index.row() == 0:
                hint.setHeight(16)
            return hint

    original_delegate = CompactLegacyDelegate(view)
    view.setItemDelegate(original_delegate)
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
    assert "QAbstractItemView { background: transparent" in popup.styleSheet()
    assert "border: none" in popup.styleSheet()
    replacement_delegate = view.itemDelegate()
    assert replacement_delegate is not original_delegate
    assert replacement_delegate.source_delegate is original_delegate

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
    assert view.visualRect(combo.model().index(0, 0)).height() == 32
    assert view.visualRect(combo.model().index(1, 0)).height() == 40
    assert view.visualRect(combo.model().index(2, 0)).height() == 32
    image = popup.grab().toImage()
    center_x = image.width() // 2
    assert image.pixelColor(center_x, 0) != image.pixelColor(center_x, 2)
    _assert_color_close(
        image.pixelColor(center_x, 2).name(),
        image.pixelColor(center_x, 3).name(),
    )
    assert image.pixelColor(center_x, image.height() - 1) != image.pixelColor(
        center_x, image.height() - 3
    )
    _assert_color_close(
        image.pixelColor(center_x, image.height() - 3).name(),
        image.pixelColor(center_x, image.height() - 4).name(),
    )

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
    assert view.itemDelegate() is original_delegate
    combo.close()


def test_native_combo_rewraps_delegate_replaced_after_adoption(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import adopt_native_widgets, disable_native_widget_styling

    disable_native_widget_styling(app, clear=True)
    combo = QtWidgets.QComboBox()
    combo.addItems(["Compact", "Default"])
    combo.resize(260, 36)
    assert adopt_native_widgets(combo) >= 1
    combo.show()
    app.processEvents()

    view = combo.view()

    class LateCompactDelegate(QtWidgets.QStyledItemDelegate):
        def sizeHint(self, option, index):
            hint = super().sizeHint(option, index)
            hint.setHeight(16)
            return hint

    late_delegate = LateCompactDelegate(view)
    view.setItemDelegate(late_delegate)
    combo.showPopup()
    app.processEvents()

    replacement = view.itemDelegate()
    assert replacement is not late_delegate
    assert replacement.source_delegate is late_delegate
    assert view.visualRect(combo.model().index(0, 0)).height() == 32

    combo.hidePopup()
    assert disable_native_widget_styling(app, clear=True) >= 1
    assert view.itemDelegate() is late_delegate
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
    size_hint_role = getattr(QtCore.Qt, "SizeHintRole", None)
    if size_hint_role is None:
        size_hint_role = QtCore.Qt.ItemDataRole.SizeHintRole
    combo.setItemData(0, QtCore.QSize(80, 16), size_hint_role)
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
    first_row = combo.view().visualRect(combo.model().index(0, 0))
    assert first_row.height() == 32
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
    from shadcn_qt._qt import QtCore

    disable_native_widget_styling(app, clear=True)
    pane = QtWidgets.QTabWidget()
    pane.setMovable(True)
    pane.setTabsClosable(True)
    original_elide_mode = pane.tabBar().elideMode()
    mac_focus_rect = getattr(QtCore.Qt, "WA_MacShowFocusRect", None)
    if mac_focus_rect is None:
        mac_focus_rect = getattr(
            QtCore.Qt.WidgetAttribute,
            "WA_MacShowFocusRect",
            None,
        )
    original_mac_focus_rect = (
        pane.tabBar().testAttribute(mac_focus_rect)
        if mac_focus_rect is not None
        else None
    )
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
    frame_overlay = pane.findChild(
        QtWidgets.QWidget,
        "shadcnQtTabPaneFrameOverlay",
    )
    assert frame_overlay is not None
    assert frame_overlay.geometry() == pane.rect()
    assert frame_overlay.property("shadcn_qt_native_styling") is False
    if mac_focus_rect is not None:
        assert not pane.tabBar().testAttribute(mac_focus_rect)
    close_buttons = [
        button
        for button in pane.tabBar().findChildren(QtWidgets.QAbstractButton)
        if button.property("tabPaneCloseButton") is True
    ]
    assert len(close_buttons) == 2

    disable_native_widget_styling(app, clear=True)
    app.processEvents()
    assert pane.property("shadcn_qt_component") is None
    assert getattr(pane, "_shadcn_qt_tab_pane_frame_overlay", None) is None
    assert frame_overlay.isHidden()
    assert pane.isMovable()
    assert pane.tabsClosable()
    assert pane.tabBar().elideMode() == original_elide_mode
    assert not pane.tabBar().hasMouseTracking()
    assert not pane.tabBar().usesScrollButtons()
    if mac_focus_rect is not None:
        assert (
            pane.tabBar().testAttribute(mac_focus_rect)
            == original_mac_focus_rect
        )
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


def test_explicit_native_tab_pane_mapping_gets_shared_painter(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import adopt_native_widgets, disable_native_widget_styling
    from shadcn_qt._qt import QtCore

    disable_native_widget_styling(app, clear=True)
    pane = QtWidgets.QTabWidget()
    pane.setProperty("shadcn_qt_component", "tab-pane")
    pane.addTab(QtWidgets.QWidget(pane), "Account")
    pane.addTab(QtWidgets.QWidget(pane), "Security")

    assert adopt_native_widgets(pane) == 1
    assert pane.property("shadcn_qt_native_adopted") is True
    assert pane.property("shadcn_qt_component") == "tab-pane"
    state = pane.property("shadcn_qt_native_enhancements")
    assert isinstance(state, dict)
    assert "tab_pane" in state

    pane.resize(420, 180)
    pane.show()
    focus_reason = getattr(QtCore.Qt, "TabFocusReason", None)
    if focus_reason is None:
        focus_reason = QtCore.Qt.FocusReason.TabFocusReason
    pane.tabBar().setFocus(focus_reason)
    app.processEvents()
    assert pane.tabBar().hasFocus()

    disable_native_widget_styling(app, clear=True)
    app.processEvents()
    assert pane.property("shadcn_qt_native_adopted") is None
    assert pane.property("shadcn_qt_component") == "tab-pane"
    pane.close()


@pytest.mark.parametrize(
    ("theme_name", "surface_color", "border_color"),
    (
        ("light", "#fafafa", "#e4e4e7"),
        ("dark", "#18181a", "#27272a"),
    ),
)
def test_native_tab_widget_initial_page_matches_active_tab_surface(
    runtime, theme_name, surface_color, border_color
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

    def assert_no_transparent_seam(y):
        assert all(
            image.pixelColor(round(x * ratio), round(y * ratio)).alpha() > 0
            for x in range(pane.width())
        )

    tab_rect = pane.tabBar().tabRect(0)
    title_color = pixel_color(tab_rect.left() + 20, tab_rect.center().y())
    page_color = pixel_color(pane.width() // 2, pane.height() // 2)
    assert title_color == surface_color
    assert page_color == title_color
    stack = pane.findChild(
        QtWidgets.QStackedWidget,
        "qt_tabwidget_stackedwidget",
    )
    frame_top = stack.geometry().top() - 1
    assert_no_transparent_seam(frame_top)
    _assert_color_close(
        pixel_color(pane.width() - 20, frame_top),
        border_color,
    )
    assert pixel_color(tab_rect.center().x(), frame_top) == surface_color
    _assert_color_close(pixel_color(0, pane.height() // 2), border_color)
    _assert_color_close(
        pixel_color(pane.width() // 2, pane.height() - 1),
        border_color,
    )

    pane.setCurrentIndex(1)
    app.processEvents()
    image = pane.grab().toImage()
    frame_top = stack.geometry().top() - 1
    assert_no_transparent_seam(frame_top)
    second_tab_rect = pane.tabBar().tabRect(1)
    _assert_color_close(
        pixel_color(tab_rect.center().x(), frame_top),
        border_color,
    )
    assert (
        pixel_color(second_tab_rect.center().x(), frame_top)
        == surface_color
    )

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


def test_native_compound_editors_keep_usable_field_at_compact_width(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import (
        adopt_native_widgets,
        apply_theme,
        disable_native_widget_styling,
    )

    disable_native_widget_styling(app, clear=True)
    apply_theme(app, "light")
    style = QtWidgets.QStyle
    spin_control = getattr(style, "CC_SpinBox", None)
    spin_edit_field = getattr(style, "SC_SpinBoxEditField", None)
    combo_control = getattr(style, "CC_ComboBox", None)
    combo_edit_field = getattr(style, "SC_ComboBoxEditField", None)
    if spin_control is None:
        spin_control = style.ComplexControl.CC_SpinBox
        spin_edit_field = style.SubControl.SC_SpinBoxEditField
        combo_control = style.ComplexControl.CC_ComboBox
        combo_edit_field = style.SubControl.SC_ComboBoxEditField

    adopted_widgets = []
    for spin_type in (QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox):
        spin = spin_type()
        spin.resize(80, 36)
        assert adopt_native_widgets(spin) >= 1
        spin.show()
        adopted_widgets.append(spin)
        app.processEvents()

        option = QtWidgets.QStyleOptionSpinBox()
        spin.initStyleOption(option)
        editor_rect = spin.style().subControlRect(
            spin_control,
            option,
            spin_edit_field,
            spin,
        )
        assert editor_rect.width() == 32
        assert spin.lineEdit().geometry() == editor_rect

    combos = (
        QtWidgets.QComboBox(),
        QtWidgets.QComboBox(),
        QtWidgets.QFontComboBox(),
    )
    combos[1].setEditable(True)
    for combo in combos:
        combo.addItems(("One", "Two"))
        combo.resize(80, 36)
        assert adopt_native_widgets(combo) >= 1
        combo.show()
        adopted_widgets.append(combo)
        app.processEvents()

        option = QtWidgets.QStyleOptionComboBox()
        combo.initStyleOption(option)
        editor_rect = combo.style().subControlRect(
            combo_control,
            option,
            combo_edit_field,
            combo,
        )
        assert editor_rect.width() == 32
        if combo.isEditable():
            assert combo.lineEdit().geometry() == editor_rect

    date = QtWidgets.QDateEdit()
    date.setCalendarPopup(True)
    temporal_editors = (
        QtWidgets.QDateEdit(),
        date,
        QtWidgets.QTimeEdit(),
        QtWidgets.QDateTimeEdit(),
    )
    for editor in temporal_editors:
        editor.resize(80, 36)
        assert adopt_native_widgets(editor) >= 1
        editor.show()
        adopted_widgets.append(editor)
        app.processEvents()
        assert editor.lineEdit().geometry().width() >= 32

    disable_native_widget_styling(app, clear=True)
    for widget in adopted_widgets:
        widget.close()


def test_native_message_box_has_balanced_reversible_layout(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import (
        adopt_native_widgets,
        apply_theme,
        disable_native_widget_styling,
    )
    from shadcn_qt._qt import QtCore

    disable_native_widget_styling(app, clear=True)
    apply_theme(app, "light")
    box = QtWidgets.QMessageBox()
    box.setWindowTitle("Confirm workspace")
    box.setText("Create the new workspace?")
    box.setInformativeText("Existing files will remain unchanged.")
    box.setStandardButtons(_message_box_buttons(QtWidgets, "Cancel", "Ok"))
    title = box.findChild(QtWidgets.QLabel, "qt_msgbox_label")
    information = box.findChild(
        QtWidgets.QLabel,
        "qt_msgbox_informativelabel",
    )
    button_box = box.findChild(
        QtWidgets.QDialogButtonBox,
        "qt_msgbox_buttonbox",
    )
    original_margins = _margins(box)
    original_title_alignment = title.alignment()
    original_information_alignment = information.alignment()
    original_title_position = _layout_position(box.layout(), title)
    original_information_position = _layout_position(box.layout(), information)
    original_layout_margins = _margins(box.layout())
    original_vertical_spacing = box.layout().verticalSpacing()
    original_button_margins = _margins(button_box.layout())

    assert adopt_native_widgets(box) >= 1
    box.show()
    app.processEvents()

    assert _margins(box) == (24, 24, 24, 24)
    assert _margins(box.layout()) == (0, 0, 0, 0)
    assert box.layout().verticalSpacing() == 8
    horizontal_center = getattr(QtCore.Qt, "AlignHCenter", None)
    align_left = getattr(QtCore.Qt, "AlignLeft", None)
    if horizontal_center is None:
        horizontal_center = QtCore.Qt.AlignmentFlag.AlignHCenter
        align_left = QtCore.Qt.AlignmentFlag.AlignLeft
    assert title.alignment() & horizontal_center
    assert information.alignment() & align_left
    assert not information.alignment() & horizontal_center
    assert title.geometry().left() == box.contentsRect().left()
    assert title.geometry().right() == box.contentsRect().right()
    assert information.geometry().left() == box.contentsRect().left()
    assert information.geometry().right() == box.contentsRect().right()
    assert _layout_position(box.layout(), title) == original_title_position
    assert (
        _layout_position(box.layout(), information)
        == original_information_position
    )
    first_button_top = min(
        button_box.geometry().top() + button.geometry().top()
        for button in button_box.buttons()
    )
    last_button_bottom = max(
        button_box.geometry().top() + button.geometry().bottom()
        for button in button_box.buttons()
    )
    assert first_button_top - information.geometry().bottom() - 1 == 24
    assert title.geometry().top() == 24
    assert box.rect().bottom() - last_button_bottom == 24

    icon_scope = getattr(QtWidgets.QMessageBox, "Icon", QtWidgets.QMessageBox)
    box.setIcon(getattr(icon_scope, "Warning"))
    app.processEvents()
    icon_label = box.findChild(QtWidgets.QLabel, "qt_msgboxex_icon_label")
    assert icon_label.pixmap() is not None
    assert not icon_label.pixmap().isNull()
    icon_title_position = _layout_position(box.layout(), title)
    icon_information_position = _layout_position(box.layout(), information)
    assert icon_title_position[1] > 0
    assert icon_information_position[1] > 0

    assert disable_native_widget_styling(app, clear=True) >= 1
    assert _margins(box) == original_margins
    title = box.findChild(QtWidgets.QLabel, "qt_msgbox_label")
    information = box.findChild(
        QtWidgets.QLabel,
        "qt_msgbox_informativelabel",
    )
    button_box = box.findChild(
        QtWidgets.QDialogButtonBox,
        "qt_msgbox_buttonbox",
    )
    assert title.alignment() == original_title_alignment
    assert information.alignment() == original_information_alignment
    assert _margins(box.layout()) == original_layout_margins
    assert box.layout().verticalSpacing() == original_vertical_spacing
    assert _margins(button_box.layout()) == original_button_margins
    assert _layout_position(box.layout(), title) == icon_title_position
    assert _layout_position(box.layout(), information) == icon_information_position
    box.close()


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


def _message_box_buttons(QtWidgets, *names):
    scope = getattr(QtWidgets.QMessageBox, "StandardButton", None)
    result = None
    for name in names:
        value = getattr(QtWidgets.QMessageBox, name, None)
        if value is None:
            value = getattr(scope, name)
        result = value if result is None else result | value
    return result


def _margins(target):
    margins = target.contentsMargins()
    return (
        margins.left(),
        margins.top(),
        margins.right(),
        margins.bottom(),
    )


def _layout_position(layout, widget):
    index = layout.indexOf(widget)
    assert index >= 0
    return tuple(layout.getItemPosition(index))
