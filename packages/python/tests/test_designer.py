import os
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def designer_runtime():
    try:
        from qtshadcn._qt import QtWidgets
    except ImportError as exc:
        pytest.skip(str(exc))

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app, QtWidgets


def test_designer_ui_loads_custom_widgets(designer_runtime):
    _, QtWidgets = designer_runtime
    from qtshadcn.designer import load_ui

    root = Path(__file__).resolve().parents[3]
    form = load_ui(root / "examples" / "python_designer" / "form.ui")
    assert type(form.saveButton).__name__ == "Button"
    assert type(form.settingsCard).__name__ == "Card"
    assert form.titleLabel.variant == "large"
    assert form.findChild(QtWidgets.QWidget, "emailInput") is form.emailInput


def test_designer_ui_restores_composite_properties(designer_runtime):
    _, QtWidgets = designer_runtime
    from qtshadcn.designer import load_ui

    root = Path(__file__).resolve().parents[3]
    form = load_ui(root / "examples" / "python_designer" / "composite.ui")
    assert type(form.activityChart).__name__ == "Chart"
    assert form.activityChart.chartType == "bar"
    assert form.activityChart.valuesList() == [8.0, 16.0, 12.0, 24.0, 20.0]
    assert form.heading.level == "h1"
    assert form.details.title == "Details"
    assert form.details.expanded is True
    assert form.pagination.currentPage == 2
    assert form.pagination.pageCount == 5
    assert form.findChild(QtWidgets.QWidget, "details") is form.details


def test_plugin_catalog_and_environment(designer_runtime):
    from qtshadcn.designer import designer_environment, designer_plugin_path
    from qtshadcn.designer.plugins import register_qtshadcn

    from qtshadcn import widgets

    assert len(register_qtshadcn.SPECS) == len(widgets.__all__)
    assert designer_plugin_path().is_dir()
    env = designer_environment({})
    assert str(designer_plugin_path()) in env["PYSIDE_DESIGNER_PLUGINS"]
    assert str(designer_plugin_path()) in env["PYQTDESIGNERPATH"]
    assert str(designer_plugin_path().parents[2]) in env["PYTHONPATH"]

    if register_qtshadcn.PLUGIN_CLASSES:
        plugin_class = register_qtshadcn.PLUGIN_CLASSES["ButtonPlugin"]
        plugin = plugin_class()
        assert plugin.name() == "Button"
        assert plugin.group() == "qtshadcn"
        assert plugin.includeFile() == "qtshadcn.widgets"
        assert 'class="Button"' in plugin.domXml()

    register_qtshadcn.apply_designer_preview()
    app = designer_runtime[0]
    preview = app.styleSheet().split("/* qtshadcn Designer preview */")[-1]
    assert "QWidget[qtshadcn_component]" in preview
    assert "QMainWindow, QDialog" not in preview
