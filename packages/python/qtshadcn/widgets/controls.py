"""Additional shadcn-aligned Qt primitives."""

from __future__ import annotations

from typing import Any, Optional, Union

from qtshadcn import _qt
from qtshadcn.widgets._helpers import (
    initialize_component,
    refresh_style,
    set_choice_property,
)

QtCore, _, QtWidgets = _qt.qt_modules()


def _text_parent(text: Any, parent: Optional[Any]) -> tuple[str, Optional[Any]]:
    if isinstance(text, QtWidgets.QWidget) and parent is None:
        return "", text
    return str(text), parent


class Label(QtWidgets.QLabel):
    VARIANTS = ("default", "muted", "lead", "large", "small")

    def __init__(
        self,
        text: Union[str, Any] = "",
        parent: Optional[Any] = None,
        *,
        variant: str = "default",
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "label")
        self._variant = "default"
        self.set_variant(variant)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, value: str) -> None:
        set_choice_property(self, "_variant", "variant", value, self.VARIANTS)

    getVariant = get_variant
    setVariant = set_variant
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)


class TextArea(QtWidgets.QPlainTextEdit):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "textarea")
        self._invalid = False

    def is_invalid(self) -> bool:
        return self._invalid

    def set_invalid(self, value: bool) -> None:
        self._invalid = bool(value)
        refresh_style(self)

    isInvalid = is_invalid
    setInvalid = set_invalid
    invalid = _qt.qt_property(bool, fget=is_invalid, fset=set_invalid)


class Checkbox(QtWidgets.QCheckBox):
    def __init__(
        self, text: Union[str, Any] = "", parent: Optional[Any] = None
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "checkbox")


class RadioButton(QtWidgets.QRadioButton):
    def __init__(
        self, text: Union[str, Any] = "", parent: Optional[Any] = None
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "radio")


class Switch(QtWidgets.QCheckBox):
    def __init__(
        self, text: Union[str, Any] = "", parent: Optional[Any] = None
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "switch")


class Select(QtWidgets.QComboBox):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "select")


class Slider(QtWidgets.QSlider):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "slider")
        horizontal = getattr(QtCore.Qt, "Horizontal", None)
        if horizontal is None:
            horizontal = QtCore.Qt.Orientation.Horizontal
        self.setOrientation(horizontal)


class Progress(QtWidgets.QProgressBar):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "progress")
        self.setTextVisible(False)


class Tabs(QtWidgets.QTabWidget):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "tabs")


class Badge(QtWidgets.QLabel):
    VARIANTS = ("default", "secondary", "outline", "destructive")

    def __init__(
        self,
        text: Union[str, Any] = "Badge",
        parent: Optional[Any] = None,
        *,
        variant: str = "default",
    ) -> None:
        text, parent = _text_parent(text, parent)
        super().__init__(text, parent)
        initialize_component(self, "badge")
        self._variant = "default"
        self.set_variant(variant)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, value: str) -> None:
        set_choice_property(self, "_variant", "variant", value, self.VARIANTS)

    getVariant = get_variant
    setVariant = set_variant
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)


class Alert(QtWidgets.QFrame):
    VARIANTS = ("default", "destructive")

    def __init__(
        self, parent: Optional[Any] = None, *, variant: str = "default"
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "alert")
        self._variant = "default"
        self.set_variant(variant)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, value: str) -> None:
        set_choice_property(self, "_variant", "variant", value, self.VARIANTS)

    getVariant = get_variant
    setVariant = set_variant
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)


class Separator(QtWidgets.QFrame):
    ORIENTATIONS = ("horizontal", "vertical")

    def __init__(
        self, parent: Optional[Any] = None, *, orientation: str = "horizontal"
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "separator")
        self._orientation_name = "horizontal"
        self.set_orientation(orientation)

    def get_orientation(self) -> str:
        return self._orientation_name

    def set_orientation(self, value: str) -> None:
        if value not in self.ORIENTATIONS:
            raise ValueError(
                f"orientation must be one of {self.ORIENTATIONS}, got {value!r}"
            )
        self._orientation_name = value
        frame = QtWidgets.QFrame
        if value == "horizontal":
            shape = getattr(frame, "HLine", None)
            if shape is None:
                shape = frame.Shape.HLine
            self.setFrameShape(shape)
            self.setFixedHeight(1)
            self.setMaximumWidth(16777215)
        else:
            shape = getattr(frame, "VLine", None)
            if shape is None:
                shape = frame.Shape.VLine
            self.setFrameShape(shape)
            self.setFixedWidth(1)
            self.setMaximumHeight(16777215)
        refresh_style(self)

    getOrientation = get_orientation
    setOrientation = set_orientation
    orientation = _qt.qt_property(str, fget=get_orientation, fset=set_orientation)


__all__ = [
    "Alert",
    "Badge",
    "Checkbox",
    "Label",
    "Progress",
    "RadioButton",
    "Select",
    "Separator",
    "Slider",
    "Switch",
    "Tabs",
    "TextArea",
]
