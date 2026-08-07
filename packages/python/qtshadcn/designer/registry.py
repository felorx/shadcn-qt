"""Widget metadata and binding-specific Qt Designer registration."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, NamedTuple, Type

from qtshadcn import _qt
from qtshadcn import widgets as widget_module
from qtshadcn._stylesheet import render_stylesheet
from qtshadcn.theme import load_theme, resolve_theme

_, QtGui, QtWidgets = _qt.qt_modules()
QtDesigner = _qt.import_qt_module("QtDesigner")

GROUP = "qtshadcn"
MODULE = "qtshadcn.widgets"


class Spec(NamedTuple):
    widget: Type[Any]
    object_name: str
    tool_tip: str
    container: bool = False
    properties_xml: str = ""


SPECS = (
    Spec(
        widget_module.Button,
        "button",
        "shadcn-style button",
        properties_xml='<property name="text"><string>Button</string></property>',
    ),
    Spec(widget_module.Input, "input", "Single-line text input"),
    Spec(widget_module.TextArea, "textArea", "Multi-line text input"),
    Spec(widget_module.Card, "card", "Card container", True),
    Spec(
        widget_module.Label,
        "label",
        "Typography label",
        properties_xml='<property name="text"><string>Label</string></property>',
    ),
    Spec(
        widget_module.Checkbox,
        "checkbox",
        "Checkbox",
        properties_xml='<property name="text"><string>Checkbox</string></property>',
    ),
    Spec(
        widget_module.RadioButton,
        "radioButton",
        "Radio button",
        properties_xml='<property name="text"><string>Radio</string></property>',
    ),
    Spec(
        widget_module.Switch,
        "switch",
        "Toggle switch",
        properties_xml='<property name="text"><string>Switch</string></property>',
    ),
    Spec(widget_module.Select, "select", "Select / combo box"),
    Spec(widget_module.Slider, "slider", "Slider"),
    Spec(
        widget_module.Progress,
        "progress",
        "Progress indicator",
        properties_xml='<property name="value"><number>40</number></property>',
    ),
    Spec(widget_module.Tabs, "tabs", "Tabbed container", True),
    Spec(
        widget_module.Badge,
        "badge",
        "Status badge",
        properties_xml='<property name="text"><string>Badge</string></property>',
    ),
    Spec(widget_module.Alert, "alert", "Alert container", True),
    Spec(widget_module.Separator, "separator", "Horizontal or vertical separator"),
)


def apply_designer_preview() -> None:
    app = QtWidgets.QApplication.instance()
    if app is None or app.property("qtshadcn_designer_preview_loaded"):
        return
    requested = os.environ.get("QTSHADCN_DESIGNER_THEME", "light")
    path = Path(requested).expanduser()
    theme = load_theme(path) if path.is_file() else resolve_theme(requested)
    preview = render_stylesheet(
        theme.colors, theme.radius, theme.font, designer_preview=True
    )
    app.setStyleSheet(
        app.styleSheet() + "\n/* qtshadcn Designer preview */\n" + preview
    )
    app.setProperty("qtshadcn_designer_preview_loaded", True)


def dom_xml(spec: Spec) -> str:
    if spec.widget.__name__ == "Tabs":
        children = """
        <widget class="QWidget" name="tab">
          <attribute name="title"><string>Tab 1</string></attribute>
        </widget>
        <widget class="QWidget" name="tab_2">
          <attribute name="title"><string>Tab 2</string></attribute>
        </widget>"""
    else:
        children = ""
    return f"""<ui language="c++">
      <widget class="{spec.widget.__name__}" name="{spec.object_name}">
        {spec.properties_xml}{children}
      </widget>
    </ui>"""


def _make_pyqt_plugin(spec: Spec) -> Type[Any]:
    base = QtDesigner.QPyDesignerCustomWidgetPlugin

    class Plugin(base):
        def __init__(self, parent: Any = None) -> None:
            super().__init__(parent)
            self._initialized = False

        def initialize(self, core: Any) -> None:
            self._initialized = True

        def isInitialized(self) -> bool:
            return self._initialized

        def createWidget(self, parent: Any) -> Any:
            apply_designer_preview()
            return spec.widget(parent)

        def name(self) -> str:
            return spec.widget.__name__

        def group(self) -> str:
            return GROUP

        def icon(self) -> Any:
            return QtGui.QIcon()

        def toolTip(self) -> str:
            return spec.tool_tip

        def whatsThis(self) -> str:
            return spec.tool_tip

        def isContainer(self) -> bool:
            return spec.container

        def domXml(self) -> str:
            return dom_xml(spec)

        def includeFile(self) -> str:
            return MODULE

    Plugin.__name__ = f"{spec.widget.__name__}Plugin"
    Plugin.__qualname__ = Plugin.__name__
    return Plugin


PLUGIN_CLASSES: Dict[str, Type[Any]] = {}
if hasattr(QtDesigner, "QPyDesignerCustomWidgetPlugin"):
    for _spec in SPECS:
        _plugin = _make_pyqt_plugin(_spec)
        PLUGIN_CLASSES[_plugin.__name__] = _plugin
        globals()[_plugin.__name__] = _plugin


def register_pyside_widgets() -> None:
    collection = QtDesigner.QPyDesignerCustomWidgetCollection
    for spec in SPECS:
        collection.registerCustomWidget(
            spec.widget,
            module=MODULE,
            tool_tip=spec.tool_tip,
            xml=dom_xml(spec),
            group=GROUP,
            container=spec.container,
        )
    apply_designer_preview()


__all__ = [
    "GROUP",
    "MODULE",
    "PLUGIN_CLASSES",
    "SPECS",
    "Spec",
    "apply_designer_preview",
    "dom_xml",
    "register_pyside_widgets",
] + list(PLUGIN_CLASSES)
