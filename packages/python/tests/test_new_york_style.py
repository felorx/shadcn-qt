import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


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
    from shadcn_qt import Button, Combobox, DatePicker, Input, NativeSelect, Select
    from shadcn_qt import TextArea, Toggle

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


def test_new_york_elevation_and_variant_contract(runtime):
    from shadcn_qt import Badge, Button, Card, Input

    assert Card().graphicsEffect() is not None
    assert Input().graphicsEffect() is not None
    assert Button("Save").graphicsEffect() is not None
    assert Button("Outline", variant="outline").graphicsEffect() is not None
    assert Button("Ghost", variant="ghost").graphicsEffect() is None
    assert Badge("New").graphicsEffect() is not None
    assert Badge("Outline", variant="outline").graphicsEffect() is None


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
    switch.setChecked(True)
    switch._animation.setCurrentTime(switch._animation.duration())
    app.processEvents()
    assert switch._thumb_position == pytest.approx(1.0)
    host.close()


def test_calendar_uses_compact_day_buttons_without_native_week_colors(runtime):
    from shadcn_qt import Calendar, apply_theme

    app, _, QtWidgets = runtime
    apply_theme(app, "light")
    calendar = Calendar()
    calendar.show()
    app.processEvents()
    view = calendar.findChild(QtWidgets.QTableView, "qt_calendar_calendarview")
    assert view.verticalHeader().defaultSectionSize() == 36
    assert type(view.itemDelegate()).__name__ == "_CalendarDelegate"
    assert not calendar.grab().isNull()
    calendar.close()


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
