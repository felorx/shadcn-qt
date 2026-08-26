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
        from shadcn_qt._qt import QtCore, QtWidgets
    except ImportError as exc:
        pytest.skip(str(exc))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app, QtCore, QtWidgets


def test_profile_identity_and_zinc_tokens(runtime):
    from shadcn_qt import BASE_COLOR, STYLE_PROFILE, apply_theme

    app, _, _ = runtime
    theme = apply_theme(app, "light")
    assert STYLE_PROFILE == "new-york"
    assert BASE_COLOR == "zinc"
    assert app.property("shadcn_qt_style") == "new-york"
    assert app.property("shadcn_qt_base_color") == "zinc"
    assert theme.colors["foreground"] == "#09090b"
    assert theme.colors["primary"] == "#18181b"
    assert theme.colors["secondary"] == "#f4f4f5"
    assert theme.colors["border"] == "#e4e4e7"


def test_new_york_control_geometry(runtime):
    from shadcn_qt import (
        Button,
        Combobox,
        DatePicker,
        Input,
        NativeSelect,
        Select,
        TextArea,
        Toggle,
    )

    assert Button("Default").height() == 36
    assert Button("Small", size="sm").height() == 32
    assert Button("Large", size="lg").height() == 40
    icon = Button("+", size="icon")
    assert (icon.width(), icon.height()) == (36, 36)
    assert Input().height() == 36
    assert TextArea().minimumHeight() == 60
    assert Toggle().height() == 36
    assert Toggle(size="sm").height() == 32
    assert Toggle(size="lg").height() == 40
    controls = (Select(), NativeSelect(), Combobox(), DatePicker())
    assert all(control.height() == 36 for control in controls)


def test_compound_editors_keep_usable_field_at_compact_width(runtime):
    from shadcn_qt import (
        Combobox,
        DatePicker,
        NativeSelect,
        Select,
        apply_theme,
    )

    app, _, QtWidgets = runtime
    apply_theme(app, "light")
    style = QtWidgets.QStyle
    combo_control = getattr(style, "CC_ComboBox", None)
    combo_edit_field = getattr(style, "SC_ComboBoxEditField", None)
    if combo_control is None:
        combo_control = style.ComplexControl.CC_ComboBox
        combo_edit_field = style.SubControl.SC_ComboBoxEditField

    for control_type in (Select, NativeSelect, Combobox):
        control = control_type()
        control.addItems(("One", "Two"))
        control.resize(80, 36)
        control.show()
        app.processEvents()

        option = QtWidgets.QStyleOptionComboBox()
        control.initStyleOption(option)
        editor_rect = control.style().subControlRect(
            combo_control,
            option,
            combo_edit_field,
            control,
        )
        assert editor_rect.width() == 32
        if control.isEditable():
            assert control.lineEdit().geometry() == editor_rect
        control.close()

    picker = DatePicker()
    picker.resize(80, 36)
    picker.show()
    app.processEvents()
    assert picker.lineEdit().geometry().width() == 32
    picker.close()


def test_choice_controls_use_shadow_xs_contract(runtime):
    del runtime
    from shadcn_qt import native
    from shadcn_qt.widgets import controls

    expected_layers = ((1.0, 3), (0.5, 4), (0.0, 6))
    assert controls._CHOICE_SHADOW_OFFSET_Y == 1.0
    assert controls._CHOICE_SHADOW_LAYERS == expected_layers
    assert native._CHOICE_SHADOW_OFFSET_Y == controls._CHOICE_SHADOW_OFFSET_Y
    assert native._CHOICE_SHADOW_LAYERS == expected_layers

    combined_opacity = 1.0
    for _, alpha in expected_layers:
        combined_opacity *= 1.0 - alpha / 255.0
    combined_opacity = 1.0 - combined_opacity
    assert combined_opacity == pytest.approx(0.05, abs=0.001)


def test_date_picker_uses_one_outer_border_and_custom_chevron(runtime):
    from shadcn_qt import DatePicker, apply_theme, theme_stylesheet
    from shadcn_qt._qt import import_qt_module

    app, QtCore, _ = runtime
    QtTest = import_qt_module("QtTest")
    apply_theme(app, "light")
    picker = DatePicker()
    picker.resize(260, 36)
    picker.show()
    picker.setFocus()
    app.processEvents()
    assert not picker.grab().isNull()
    assert picker.hasMouseTracking()
    normal_image = picker.grab().toImage()
    picker._set_drop_down_hovered(True)
    app.processEvents()
    hovered_image = picker.grab().toImage()
    ratio = hovered_image.devicePixelRatio()
    hover_sample_x = int((picker.width() - 28) * ratio)
    hover_sample_y = int((picker.height() / 2) * ratio)
    assert normal_image.pixelColor(
        hover_sample_x, hover_sample_y
    ) != hovered_image.pixelColor(hover_sample_x, hover_sample_y)

    left_button = getattr(QtCore.Qt, "LeftButton", None)
    if left_button is None:
        left_button = QtCore.Qt.MouseButton.LeftButton
    QtTest.QTest.mouseClick(
        picker,
        left_button,
        pos=QtCore.QPoint(picker.width() - 16, picker.height() // 2),
    )
    app.processEvents()
    calendar_popup = picker.calendarWidget().window()
    expected_popup_position = picker.mapToGlobal(
        QtCore.QPoint(0, picker.height())
    )
    assert calendar_popup.pos() == expected_popup_position
    calendar_popup.hide()

    qss = theme_stylesheet("light")
    selector = 'QDateTimeEdit[shadcn_qt_component="date-picker"]::drop-down'
    assert selector in qss
    rule = qss.split(selector, 1)[1].split("}", 1)[0]
    assert "border: none" in rule
    assert "background: transparent" in rule
    assert 'QDateTimeEdit[shadcn_qt_component="date-picker"]::down-arrow' in qss


def test_combo_family_popups_use_one_outer_border(runtime):
    from shadcn_qt import Combobox, NativeSelect, Select, apply_theme, theme_stylesheet
    from shadcn_qt._qt import import_qt_module

    app, QtCore, _ = runtime
    QtTest = import_qt_module("QtTest")
    left_button = getattr(QtCore.Qt, "LeftButton", None)
    if left_button is None:
        left_button = QtCore.Qt.MouseButton.LeftButton
    apply_theme(app, "light")
    for control_type in (Select, Combobox, NativeSelect):
        control = control_type()
        control.addItems(["Apple", "Banana", "Cherry"])
        control.resize(260, 36)
        control.show()
        app.processEvents()
        controller = control._shadcn_qt_combo_chevron
        glyph = controller.glyph
        icon_bounds = glyph._icon_path().boundingRect()
        expected_size = (6.0, 10.0) if control.isEditable() else (8.0, 4.0)
        assert (icon_bounds.width(), icon_bounds.height()) == expected_size
        assert icon_bounds.center() == QtCore.QRectF(glyph.rect()).center()
        if control.isEditable():
            QtTest.QTest.mouseClick(
                control.lineEdit(),
                left_button,
                pos=control.lineEdit().rect().center(),
            )
            app.processEvents()
            assert not control.view().isVisible()
            trigger_point = glyph.geometry().center()
        else:
            trigger_point = control.rect().center()
        QtTest.QTest.mousePress(
            control,
            left_button,
            pos=trigger_point,
        )
        app.processEvents()
        assert not control.view().isVisible()
        QtTest.QTest.mouseRelease(
            control,
            left_button,
            pos=trigger_point,
        )
        app.processEvents()
        assert control.view().isVisible()
        popup = control.view().window()
        assert popup.objectName() == "shadcnQtComboPopup"
        assert "border: 1px solid #e4e4e7" in popup.styleSheet()
        assert popup.width() == control.width()
        expected_popup_position = control.mapToGlobal(
            QtCore.QPoint(0, control.height())
        )
        assert popup.pos() == expected_popup_position
        second_row = control.view().visualRect(control.model().index(1, 0))
        assert second_row.height() == 32
        assert second_row.width() <= control.view().viewport().width()
        image = popup.grab().toImage()
        center_x = image.width() // 2
        assert image.pixelColor(center_x, 0) != image.pixelColor(center_x, 2)
        assert image.pixelColor(center_x, image.height() - 1) != image.pixelColor(
            center_x, image.height() - 3
        )
        QtTest.QTest.mouseClick(
            control.view().viewport(),
            left_button,
            pos=second_row.center(),
        )
        app.processEvents()
        assert control.currentText() == "Banana"
        assert not control.view().isVisible()
        control.close()

    qss = theme_stylesheet("light")
    selector = "QComboBox[shadcn_qt_component] QAbstractItemView"
    rule = qss.split(selector, 1)[1].split("}", 1)[0]
    assert "background: transparent" in rule
    assert "border: none" in rule
    assert "QComboBox[shadcn_qt_component]::down-arrow" in qss
    assert "QComboBox[shadcn_qt_component] QAbstractItemView::item" in qss
    drop_down_rule = qss.split(
        "QComboBox[shadcn_qt_component]::drop-down", 1
    )[1].split("}", 1)[0]
    assert "margin: 2px" in drop_down_rule
    assert "border-radius: 4px" in drop_down_rule
    assert "QComboBox[shadcn_qt_component]::drop-down:hover" in qss


def test_combo_popup_rows_enforce_minimum_and_preserve_larger_hints(runtime):
    from shadcn_qt import Combobox, NativeSelect, Select, apply_theme

    app, QtCore, _ = runtime
    size_hint_role = getattr(QtCore.Qt, "SizeHintRole", None)
    if size_hint_role is None:
        size_hint_role = QtCore.Qt.ItemDataRole.SizeHintRole
    apply_theme(app, "light")

    for control_type in (Select, Combobox, NativeSelect):
        control = control_type()
        control.addItems(["Compact", "Default", "Spacious"])
        control.setItemData(0, QtCore.QSize(80, 16), size_hint_role)
        control.setItemData(2, QtCore.QSize(80, 40), size_hint_role)
        control.resize(260, 36)
        control.show()
        control.showPopup()
        app.processEvents()

        heights = [
            control.view().visualRect(control.model().index(row, 0)).height()
            for row in range(3)
        ]
        assert heights == [32, 32, 40]

        control.hidePopup()
        control.close()


def test_dropdown_menu_opens_left_aligned_directly_below(runtime):
    from shadcn_qt import Button, DropdownMenu

    app, QtCore, QtWidgets = runtime
    host = QtWidgets.QWidget()
    host.setGeometry(100, 100, 600, 300)
    trigger = Button("Open menu", host, variant="outline")
    trigger.setGeometry(70, 60, 180, 36)
    menu = DropdownMenu("Account", host)
    menu.addItem("Profile")
    menu.addItem("Billing")
    host.show()
    app.processEvents()

    menu.showAt(trigger)
    app.processEvents()

    expected_popup_position = trigger.mapToGlobal(
        QtCore.QPoint(0, trigger.height())
    )
    assert menu.pos() == expected_popup_position

    menu.close()
    host.close()


def test_new_york_elevation_and_variant_contract(runtime):
    from shadcn_qt import Badge, Button, Card, Input

    assert Card().graphicsEffect() is not None
    assert Input().graphicsEffect() is not None
    assert Button("Save").graphicsEffect() is not None
    assert Button("Outline", variant="outline").graphicsEffect() is not None
    assert Button("Ghost", variant="ghost").graphicsEffect() is None
    assert Badge("New").graphicsEffect() is not None
    assert Badge("Outline", variant="outline").graphicsEffect() is None


def test_new_york_shadows_remain_short_and_low_opacity(runtime):
    from shadcn_qt import Button, Card, Dialog, Input

    controls = (Input(), Button("Save"), Card(), Dialog())
    expected = ((2.0, 13), (4.0, 16), (4.0, 16), (20.0, 24))
    for widget, (blur, alpha) in zip(controls, expected):
        effect = widget.graphicsEffect()
        assert effect.blurRadius() == blur
        assert effect.yOffset() <= 6.0
        assert effect.color().alpha() == alpha


def test_custom_selection_controls_render_and_switch_animates(runtime):
    from shadcn_qt import Checkbox, RadioButton, Switch, apply_theme

    app, _, QtWidgets = runtime
    apply_theme(app, "light")
    host = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(host)
    checkbox = Checkbox("Checked", host)
    checkbox.setChecked(True)
    radio = RadioButton("Selected", host)
    radio.setChecked(True)
    switch = Switch("Enabled", host)
    layout.addWidget(checkbox)
    layout.addWidget(radio)
    layout.addWidget(switch)
    host.show()
    app.processEvents()
    assert all(not widget.grab().isNull() for widget in (checkbox, radio, switch))
    from shadcn_qt.widgets.controls import _choice_geometry

    assert _choice_geometry(checkbox, 16)[0].left() == 3
    assert _choice_geometry(radio, 16)[0].left() == 3
    for widget, indicator_size in ((checkbox, 16), (radio, 16), (switch, 36)):
        indicator = _choice_geometry(widget, indicator_size)[0]
        if widget is switch:
            indicator.setHeight(20)
            indicator.moveTop((widget.height() - 20) / 2)
        bounds = indicator.adjusted(-1.5, -1.5, 1.5, 1.5)
        assert bounds.left() >= 0.5
        assert bounds.top() >= 0.5
        assert bounds.right() <= widget.width() - 0.5
        assert bounds.bottom() <= widget.height() - 0.5
    switch.setChecked(True)
    switch._animation.setCurrentTime(switch._animation.duration())
    app.processEvents()
    assert switch._thumb_position == pytest.approx(1.0)
    host.close()


def test_calendar_uses_compact_day_buttons_without_native_week_colors(runtime):
    from shadcn_qt import Calendar, apply_theme, theme_stylesheet

    app, QtCore, QtWidgets = runtime
    apply_theme(app, "light")
    calendar = Calendar()
    calendar.show()
    app.processEvents()
    view = calendar.findChild(QtWidgets.QTableView, "qt_calendar_calendarview")
    assert view.verticalHeader().defaultSectionSize() == 36
    assert type(view.itemDelegate()).__name__ == "_CalendarDelegate"
    month_button = calendar.findChild(
        QtWidgets.QToolButton, "qt_calendar_monthbutton"
    )
    assert month_button.icon().isNull()
    indicator = calendar._month_indicator
    assert indicator.parent() is month_button
    assert indicator.geometry().top() == 0
    assert indicator.geometry().bottom() == month_button.rect().bottom()
    icon_bounds = indicator._icon_path().boundingRect()
    assert (icon_bounds.width(), icon_bounds.height()) == (8.0, 4.0)
    assert icon_bounds.center() == QtCore.QRectF(indicator.rect()).center()
    navigation_buttons = (
        calendar.findChild(QtWidgets.QToolButton, "qt_calendar_prevmonth"),
        calendar.findChild(QtWidgets.QToolButton, "qt_calendar_nextmonth"),
    )
    assert len(calendar._navigation_indicators) == 2
    for button, navigation_indicator, accessible_name in zip(
        navigation_buttons,
        calendar._navigation_indicators,
        ("Previous month", "Next month"),
    ):
        assert button.text() == ""
        assert button.accessibleName() == accessible_name
        assert navigation_indicator.geometry() == button.rect()
        navigation_bounds = navigation_indicator._icon_path().boundingRect()
        assert (navigation_bounds.width(), navigation_bounds.height()) == (4.0, 8.0)
        assert navigation_bounds.center() == QtCore.QRectF(
            navigation_indicator.rect()
        ).center()
    qss = theme_stylesheet("light")
    assert (
        'QToolButton#qt_calendar_monthbutton::menu-indicator { image: none; '
        "width: 0; height: 0; }"
    ) in qss
    assert not calendar.grab().isNull()
    calendar.close()


def test_item_hover_surface_and_action_icon_stay_visually_aligned(runtime):
    from shadcn_qt import Item, apply_theme, theme_stylesheet

    app, QtCore, _ = runtime
    apply_theme(app, "light")
    item = Item(title="Documentation", description="Installation and themes")
    item.resize(520, item.sizeHint().height())
    item.show()
    app.processEvents()
    assert item.content.objectName() == "shadcnQtItemContent"
    assert not item.content.autoFillBackground()
    assert not item.actionContainer.autoFillBackground()
    icon_bounds = item.action._icon_path().boundingRect()
    assert (icon_bounds.width(), icon_bounds.height()) == (4.0, 8.0)
    assert icon_bounds.center() == QtCore.QRectF(item.action.rect()).center()
    assert (item.action.width(), item.action.height()) == (36, 36)
    assert item.action.geometry() == item.actionContainer.rect()
    assert (
        QtCore.QRectF(item.actionContainer.geometry()).center().y()
        == QtCore.QRectF(item.rect()).center().y()
    )
    assert item.action.accessibleName() == "Open item"
    assert not item.grab().isNull()
    qss = theme_stylesheet("light")
    assert (
        'QFrame[shadcn_qt_component="item"] QWidget#shadcnQtItemContent'
        in qss
    )
    assert 'QFrame[shadcn_qt_component="item"] QLabel { background: transparent; }' in qss
    item.close()


def test_dialog_uses_frameless_modal_surface(runtime):
    from shadcn_qt import Dialog

    _, QtCore, QtWidgets = runtime
    parent = QtWidgets.QWidget()
    dialog = Dialog(parent)
    frameless = getattr(QtCore.Qt, "FramelessWindowHint", None)
    if frameless is None:
        frameless = QtCore.Qt.WindowType.FramelessWindowHint
    assert dialog.isModal()
    assert bool(dialog.windowFlags() & frameless)
    assert dialog._overlay.parent() is parent
    assert dialog.graphicsEffect() is not None
    assert dialog.layout_.contentsMargins().left() == 24
    dialog.close()


def test_stylesheet_contains_new_york_states_without_legacy_shortcuts(runtime):
    from shadcn_qt import theme_stylesheet

    qss = theme_stylesheet("light")
    assert "classic new-york + Zinc" in qss
    assert 'shadcnSize="sm"' in qss
    assert 'shadcn_qt_component="dialog-overlay"' in qss
    assert "border-radius: 12px" in qss
    assert "text-decoration: none" in qss
    assert "padding-top: 9px" not in qss
    assert 'elevated="true"] {\n  border: 2px' not in qss


def test_tab_pane_uses_scoped_chrome_style(runtime):
    from shadcn_qt import TabPane, Tabs, theme_stylesheet

    _, _, QtWidgets = runtime
    pane = TabPane()
    tabs = Tabs()
    assert isinstance(pane, QtWidgets.QTabWidget)
    assert pane.property("shadcn_qt_component") == "tab-pane"
    assert tabs.property("shadcn_qt_component") == "tabs"

    qss = theme_stylesheet("light")
    dark_qss = theme_stylesheet("dark")
    assert "Chrome-style document tabs" in qss
    assert (
        'QTabWidget[shadcn_qt_component="tab-pane"] '
        "QTabBar::tab:selected"
    ) in qss
    assert (
        'QTabBar[shadcn_qt_component="tab-pane-bar"]::close-button:hover'
        in qss
    )
    assert (
        'QTabWidget[shadcn_qt_component="tabs"] QTabBar::tab:selected'
        in qss
    )
    assert "border-top: 0" in qss
    assert "border-bottom-color:" in qss
    assert "margin-bottom: -1px" in qss
    assert "border-bottom-color: #f4f4f5" in qss
    assert "QTabBar::tab:first" in qss
    assert "margin-left: 10px" in qss
    assert "background: #fafafa; border: 1px" in qss
    assert "background: #18181a; border: 1px" in dark_qss
    assert "background: transparent; border: none; padding: 3px" in qss
    assert (
        'QTabWidget[shadcn_qt_component="tab-pane"] '
        "QTabBar::tab:focus"
    ) not in qss
    assert (
        'QTabBar[shadcn_qt_component="tab-pane-bar"]::tab:focus'
        not in qss
    )
    assert "\nQTabBar {" not in qss


@pytest.mark.parametrize(
    ("theme_name", "surface_color", "border_color"),
    (
        ("light", "#fafafa", "#e4e4e7"),
        ("dark", "#18181a", "#27272a"),
    ),
)
def test_tab_pane_active_title_and_page_share_surface(
    runtime, theme_name, surface_color, border_color
):
    from shadcn_qt import TabPane, apply_theme, theme_stylesheet

    app, _, QtWidgets = runtime
    apply_theme(app, theme_name)
    pane = TabPane()
    pane.resize(420, 180)
    page = QtWidgets.QWidget(pane)
    # Match Gallery/native-adapter behavior: otherwise the default transparent
    # page does not exercise the rule that previously covered the pane surface.
    page.setProperty("shadcn_qt_component", "widget")
    page.setProperty("shadcn_qt_native_adopted", True)
    pane.addTab(page, "Account")
    second_page = QtWidgets.QWidget(pane)
    second_page.setProperty("shadcn_qt_component", "widget")
    second_page.setProperty("shadcn_qt_native_adopted", True)
    pane.addTab(second_page, "Security")
    pane.show()
    app.processEvents()

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
    assert (
        'QTabWidget[shadcn_qt_component="tab-pane"] '
        "QStackedWidget#qt_tabwidget_stackedwidget > QWidget"
    ) in theme_stylesheet(theme_name)
    pane.close()


@pytest.mark.parametrize("native", (False, True))
def test_tab_pane_focus_uses_outer_outline_without_title_pill(runtime, native):
    from shadcn_qt import (
        TabPane,
        adopt_native_widgets,
        apply_theme,
        disable_native_widget_styling,
    )
    from shadcn_qt.widgets._tab_pane import _tab_body_rect

    app, QtCore, QtWidgets = runtime
    disable_native_widget_styling(app, clear=True)
    apply_theme(app, "light")
    pane = QtWidgets.QTabWidget() if native else TabPane()
    file_icon = getattr(QtWidgets.QStyle, "SP_FileIcon", None)
    if file_icon is None:
        file_icon = QtWidgets.QStyle.StandardPixmap.SP_FileIcon
    icon = app.style().standardIcon(file_icon)
    pane.addTab(QtWidgets.QWidget(pane), icon, "Overview")
    pane.addTab(QtWidgets.QWidget(pane), icon, "Settings")
    if native:
        adopt_native_widgets(pane)
    pane.resize(500, 200)
    pane.show()
    focus_reason = getattr(QtCore.Qt, "TabFocusReason", None)
    if focus_reason is None:
        focus_reason = QtCore.Qt.FocusReason.TabFocusReason
    pane.tabBar().setFocus(focus_reason)
    app.processEvents()

    assert pane.tabBar().hasFocus()
    image = pane.grab().toImage()
    ratio = image.devicePixelRatio()
    title_rect = _tab_body_rect(pane.tabBar(), 0).adjusted(0, 2, 0, 0)
    former_focus_rect = title_rect.adjusted(3, 3, -3, -3)

    def pixel_color(x, y):
        return image.pixelColor(round(x * ratio), round(y * ratio)).name()

    inner_edge_color = pixel_color(
        former_focus_rect.left(),
        former_focus_rect.center().y(),
    )
    nearby_surface_color = pixel_color(
        former_focus_rect.left() + 5,
        former_focus_rect.center().y(),
    )
    assert inner_edge_color == nearby_surface_color

    pane.close()
    disable_native_widget_styling(app, clear=True)
