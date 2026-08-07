"""Opt-in styling for existing native Qt widgets.

The adapter adds the same dynamic properties used by qtshadcn subclasses to
compatible standard widgets.  It deliberately supplies only safe defaults;
semantic choices such as Card vs Alert or Checkbox vs Switch remain explicit.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional, Tuple

from qtshadcn import _qt

_ADAPTER_ATTRIBUTE = "_qtshadcn_native_widget_styling_adapter"
_ADOPTED_PROPERTY = "qtshadcn_native_adopted"
_ADDED_PROPERTIES = "qtshadcn_native_properties"
_PREFERENCE_PROPERTY = "qtshadcn_native_styling"
_STYLE_PROPERTIES = frozenset(
    {"qtshadcn_component", "variant", "shadcnSize", "invalid"}
)
_ADAPTER_TYPE: Optional[Any] = None


def _refresh_style(widget: Any) -> None:
    style = widget.style()
    if style is not None:
        style.unpolish(widget)
        style.polish(widget)
    widget.update()


def _is_internal_widget(widget: Any, widgets: Any) -> bool:
    name = widget.objectName()
    if name and name.startswith("qt_"):
        return True
    if isinstance(widget, widgets.QLineEdit):
        parent = widget.parentWidget()
        if isinstance(parent, (widgets.QComboBox, widgets.QAbstractSpinBox)):
            return True
    return False


def _native_defaults(widget: Any, widgets: Any) -> Optional[Dict[str, Any]]:
    """Return the default qtshadcn properties for a native widget type."""

    specs: Iterable[Tuple[Any, str, Dict[str, Any]]] = (
        (
            widgets.QPushButton,
            "button",
            {"variant": "default", "shadcnSize": "default"},
        ),
        (widgets.QLineEdit, "input", {"invalid": False}),
        (widgets.QPlainTextEdit, "textarea", {"invalid": False}),
        (widgets.QCheckBox, "checkbox", {}),
        (widgets.QRadioButton, "radio", {}),
        (widgets.QDateEdit, "date-picker", {}),
        (widgets.QComboBox, "select", {}),
        (widgets.QSlider, "slider", {}),
        (widgets.QProgressBar, "progress", {}),
        (widgets.QTabWidget, "tabs", {}),
        (widgets.QTableWidget, "table", {}),
        (widgets.QTableView, "data-table", {}),
        (widgets.QCalendarWidget, "calendar", {}),
        (widgets.QScrollArea, "scroll-area", {}),
        (widgets.QMenuBar, "menubar", {}),
        (widgets.QLabel, "label", {"variant": "default"}),
    )
    for widget_type, component, defaults in specs:
        if isinstance(widget, widget_type):
            return {"qtshadcn_component": component, **defaults}
    return None


def _preference(widget: Any) -> Optional[bool]:
    value = widget.property(_PREFERENCE_PROPERTY)
    if value is None:
        return None
    return bool(value)


def _adopt_widget(widget: Any, widgets: Any, *, refresh: bool) -> bool:
    if widget.property(_ADOPTED_PROPERTY):
        return False
    preference = _preference(widget)
    if preference is False:
        return False
    if widget.property("qtshadcn_component") not in (None, ""):
        return False
    if preference is not True and _is_internal_widget(widget, widgets):
        return False
    defaults = _native_defaults(widget, widgets)
    if defaults is None:
        return False

    added = []
    for name, value in defaults.items():
        if widget.property(name) is None:
            widget.setProperty(name, value)
            added.append(name)
    if not added:
        return False

    widget.setProperty(_ADOPTED_PROPERTY, True)
    widget.setProperty(_ADDED_PROPERTIES, ",".join(added))
    if refresh:
        _refresh_style(widget)
    return True


def _clear_widget(widget: Any, widgets: Any, *, refresh: bool) -> bool:
    if not widget.property(_ADOPTED_PROPERTY):
        return False
    defaults = _native_defaults(widget, widgets) or {}
    names = str(widget.property(_ADDED_PROPERTIES) or "").split(",")
    # Clear the marker first so property-change events below are not mistaken
    # for user customization that needs a separate repolish.
    widget.setProperty(_ADOPTED_PROPERTY, None)
    for name in (item for item in names if item):
        if name in defaults and widget.property(name) == defaults[name]:
            widget.setProperty(name, None)
    widget.setProperty(_ADDED_PROPERTIES, None)
    if refresh:
        _refresh_style(widget)
    return True


def _widgets_below(root: Any, widgets: Any, *, recursive: bool) -> Iterable[Any]:
    if isinstance(root, widgets.QApplication):
        return tuple(root.allWidgets())
    if isinstance(root, widgets.QWidget):
        if not recursive:
            return (root,)
        return (root, *root.findChildren(widgets.QWidget))
    raise TypeError("root must be a QApplication or QWidget")


def adopt_native_widgets(
    root: Any,
    *,
    recursive: bool = True,
    refresh: bool = True,
) -> int:
    """Apply qtshadcn default component properties below ``root``.

    Explicit ``qtshadcn_component`` values and widgets with
    ``qtshadcn_native_styling=False`` are left unchanged.  The return value is
    the number of widgets newly adopted.
    """

    _, _, widgets = _qt.qt_modules()
    return sum(
        _adopt_widget(widget, widgets, refresh=refresh)
        for widget in _widgets_below(root, widgets, recursive=recursive)
    )


def _event_property_name(event: Any) -> str:
    value = event.propertyName()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    data = getattr(value, "data", None)
    if callable(data):
        raw = data()
        if isinstance(raw, bytes):
            return raw.decode("utf-8", errors="replace")
    return str(value)


def _adapter_type() -> Any:
    global _ADAPTER_TYPE
    if _ADAPTER_TYPE is not None:
        return _ADAPTER_TYPE

    core, _, widgets = _qt.qt_modules()
    polish = getattr(core.QEvent, "Polish", None)
    dynamic_change = getattr(core.QEvent, "DynamicPropertyChange", None)
    if polish is None:
        polish = core.QEvent.Type.Polish
        dynamic_change = core.QEvent.Type.DynamicPropertyChange

    class NativeWidgetStylingAdapter(core.QObject):
        def eventFilter(self, watched: Any, event: Any) -> bool:
            if not isinstance(watched, widgets.QWidget):
                return False
            if event.type() == polish:
                _adopt_widget(watched, widgets, refresh=False)
            elif (
                event.type() == dynamic_change
                and _event_property_name(event) == _PREFERENCE_PROPERTY
            ):
                if _preference(watched) is False:
                    _clear_widget(watched, widgets, refresh=True)
                else:
                    _adopt_widget(watched, widgets, refresh=True)
            elif (
                event.type() == dynamic_change
                and _event_property_name(event) in _STYLE_PROPERTIES
                and watched.property(_ADOPTED_PROPERTY)
            ):
                _refresh_style(watched)
            return False

    _ADAPTER_TYPE = NativeWidgetStylingAdapter
    return _ADAPTER_TYPE


def enable_native_widget_styling(app: Any = None) -> Any:
    """Continuously adopt existing and future compatible native widgets."""

    _, _, widgets = _qt.qt_modules()
    if app is None:
        app = widgets.QApplication.instance()
    if app is None:
        raise RuntimeError("No QApplication instance; create QApplication first.")
    if not isinstance(app, widgets.QApplication):
        raise TypeError("app must be a QApplication")

    existing = getattr(app, _ADAPTER_ATTRIBUTE, None)
    if existing is not None:
        return existing
    adapter = _adapter_type()(app)
    app.installEventFilter(adapter)
    setattr(app, _ADAPTER_ATTRIBUTE, adapter)
    app.setProperty("qtshadcn_native_styling_enabled", True)
    adopt_native_widgets(app)
    return adapter


def disable_native_widget_styling(app: Any = None, *, clear: bool = True) -> int:
    """Stop automatic adoption and optionally remove unchanged adapter defaults."""

    _, _, widgets = _qt.qt_modules()
    if app is None:
        app = widgets.QApplication.instance()
    if app is None:
        raise RuntimeError("No QApplication instance; create QApplication first.")
    if not isinstance(app, widgets.QApplication):
        raise TypeError("app must be a QApplication")

    adapter = getattr(app, _ADAPTER_ATTRIBUTE, None)
    if adapter is not None:
        app.removeEventFilter(adapter)
        delattr(app, _ADAPTER_ATTRIBUTE)
        adapter.deleteLater()
    app.setProperty("qtshadcn_native_styling_enabled", False)

    cleared = 0
    if clear:
        for widget in tuple(app.allWidgets()):
            cleared += int(_clear_widget(widget, widgets, refresh=True))
    return cleared


__all__ = [
    "adopt_native_widgets",
    "disable_native_widget_styling",
    "enable_native_widget_styling",
]
