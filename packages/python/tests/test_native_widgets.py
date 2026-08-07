import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="module")
def runtime():
    try:
        from qtshadcn._qt import QtWidgets
    except ImportError as exc:
        pytest.skip(str(exc))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app, QtWidgets


def test_adopt_native_widgets_preserves_explicit_choices(runtime):
    app, QtWidgets = runtime
    from qtshadcn import Button, adopt_native_widgets

    root = QtWidgets.QWidget()
    button = QtWidgets.QPushButton("Save", root)
    button.setProperty("variant", "outline")
    line_edit = QtWidgets.QLineEdit(root)
    checkbox = QtWidgets.QCheckBox(root)
    opted_out = QtWidgets.QPushButton("Native", root)
    opted_out.setProperty("qtshadcn_native_styling", False)
    custom = Button("Already qtshadcn", root)

    combo = QtWidgets.QComboBox(root)
    combo.setEditable(True)
    internal_line_edit = combo.lineEdit()

    adopted = adopt_native_widgets(root)

    assert adopted >= 4
    assert button.property("qtshadcn_component") == "button"
    assert button.property("variant") == "outline"
    assert button.property("shadcnSize") == "default"
    assert line_edit.property("qtshadcn_component") == "input"
    assert checkbox.property("qtshadcn_component") == "checkbox"
    assert combo.property("qtshadcn_component") == "select"
    assert internal_line_edit.property("qtshadcn_component") is None
    assert opted_out.property("qtshadcn_component") is None
    assert custom.property("qtshadcn_native_adopted") is None

    # Clear markers added by the scoped operation before the global test.
    from qtshadcn import disable_native_widget_styling

    assert disable_native_widget_styling(app, clear=True) >= adopted


def test_global_adapter_handles_future_widgets_and_opt_out(runtime):
    app, QtWidgets = runtime
    from qtshadcn import (
        disable_native_widget_styling,
        enable_native_widget_styling,
    )

    disable_native_widget_styling(app, clear=True)
    existing = QtWidgets.QPushButton("Existing")
    adapter = enable_native_widget_styling(app)
    assert adapter is enable_native_widget_styling(app)
    assert existing.property("qtshadcn_component") == "button"
    assert app.property("qtshadcn_native_styling_enabled") is True

    future = QtWidgets.QPushButton("Future")
    future.ensurePolished()
    app.processEvents()
    assert future.property("qtshadcn_component") == "button"
    assert future.property("variant") == "default"
    assert future.property("shadcnSize") == "default"

    future.setProperty("qtshadcn_native_styling", False)
    assert future.property("qtshadcn_component") is None
    assert future.property("variant") is None

    future.setProperty("qtshadcn_native_styling", True)
    assert future.property("qtshadcn_component") == "button"
    future.setProperty("variant", "destructive")

    cleared = disable_native_widget_styling(app, clear=True)
    assert cleared >= 2
    assert existing.property("qtshadcn_component") is None
    assert future.property("qtshadcn_component") is None
    # User changes made after adoption are not deleted during cleanup.
    assert future.property("variant") == "destructive"
    assert app.property("qtshadcn_native_styling_enabled") is False

    after_disable = QtWidgets.QPushButton("After disable")
    after_disable.ensurePolished()
    app.processEvents()
    assert after_disable.property("qtshadcn_component") is None
