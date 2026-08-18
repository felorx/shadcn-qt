import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="module")
def qt():
    try:
        from shadcn_qt._qt import QtWidgets
    except ImportError as exc:
        pytest.skip(str(exc))

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app, QtWidgets


def test_widget_catalog_and_designer_properties(qt):
    app, QtWidgets = qt
    from shadcn_qt import (
        Alert,
        Badge,
        Button,
        Card,
        Checkbox,
        Input,
        Label,
        Progress,
        RadioButton,
        Select,
        Separator,
        Slider,
        Switch,
        Tabs,
        TextArea,
        apply_theme,
    )

    parent = QtWidgets.QWidget()
    button = Button(parent)
    assert button.parent() is parent
    assert button.setProperty("variant", "outline")
    assert button.setProperty("shadcnSize", "sm")
    assert button.variant == "outline"
    assert button.shadcnSize == "sm"
    assert button.metaObject().indexOfProperty("variant") >= 0

    instances = [
        Alert(),
        Badge(),
        button,
        Card(),
        Checkbox(),
        Input(),
        Label(),
        Progress(),
        RadioButton(),
        Select(),
        Separator(),
        Slider(),
        Switch(),
        Tabs(),
        TextArea(),
    ]
    assert all(widget.property("shadcn_qt_component") for widget in instances)
    applied = apply_theme(
        app,
        "dark",
        colors={"primary": "#7c3aed"},
        radius_base=9,
    )
    assert applied.colors["primary"] == "#7c3aed"
    assert applied.radius == {
        "sm": "6px",
        "md": "9px",
        "lg": "12px",
        "xl": "18px",
    }
    assert app.property("shadcn_qt_radius_sm") == "6px"
    assert app.property("shadcn_qt_radius_md") == "9px"
    assert app.property("shadcn_qt_radius_lg") == "12px"
    assert app.property("shadcn_qt_radius_xl") == "18px"
    from shadcn_qt.widgets._style import semantic_radius

    assert semantic_radius(button, "sm") == 6.0
    assert semantic_radius(button, "md") == 9.0
    assert semantic_radius(button, "lg") == 12.0
    assert semantic_radius(button, "xl") == 18.0
    assert "#7c3aed" in app.styleSheet()
