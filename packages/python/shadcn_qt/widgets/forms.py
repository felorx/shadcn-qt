"""Composed form controls aligned with shadcn/ui."""

from __future__ import annotations

from typing import Any, Iterable, Optional, Union

from shadcn_qt import _qt
from shadcn_qt.widgets._helpers import initialize_component, refresh_style
from shadcn_qt.widgets.button import Button
from shadcn_qt.widgets.controls import Label, RadioButton
from shadcn_qt.widgets.input import Input

QtCore, _, QtWidgets = _qt.qt_modules()


def _align_center() -> Any:
    value = getattr(QtCore.Qt, "AlignCenter", None)
    return value if value is not None else QtCore.Qt.AlignmentFlag.AlignCenter


class Toggle(QtWidgets.QToolButton):
    VARIANTS = ("default", "outline")

    def __init__(
        self,
        text: Union[str, Any] = "",
        parent: Optional[Any] = None,
        *,
        variant: str = "default",
    ) -> None:
        if isinstance(text, QtWidgets.QWidget) and parent is None:
            parent, text = text, ""
        super().__init__(parent)
        initialize_component(self, "toggle")
        self.setText(str(text))
        self.setCheckable(True)
        self._variant = "default"
        self.set_variant(variant)

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, variant: str) -> None:
        if variant not in self.VARIANTS:
            raise ValueError(f"variant must be one of {self.VARIANTS}")
        self._variant = variant
        refresh_style(self)

    getVariant = get_variant
    setVariant = set_variant
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)


class ToggleGroup(QtWidgets.QFrame):
    valueChanged = _qt.qt_signal(str)

    def __init__(self, parent: Optional[Any] = None, *, exclusive: bool = True) -> None:
        super().__init__(parent)
        initialize_component(self, "toggle-group")
        self._buttons = {}
        self._layout = QtWidgets.QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.group = QtWidgets.QButtonGroup(self)
        self.group.setExclusive(exclusive)

    def addItem(self, value: str, text: Optional[str] = None) -> Toggle:
        button = Toggle(text or value, self, variant="outline")
        button.toggled.connect(
            lambda checked, item=value: checked and self.valueChanged.emit(item)
        )
        self._buttons[value] = button
        self.group.addButton(button)
        self._layout.addWidget(button)
        return button

    def value(self) -> str:
        for value, button in self._buttons.items():
            if button.isChecked():
                return value
        return ""

    def setValue(self, value: str) -> None:
        if value in self._buttons:
            self._buttons[value].setChecked(True)

    def isExclusive(self) -> bool:
        return self.group.exclusive()

    def setExclusive(self, exclusive: bool) -> None:
        self.group.setExclusive(bool(exclusive))

    exclusive = _qt.qt_property(bool, fget=isExclusive, fset=setExclusive)


class ButtonGroup(QtWidgets.QFrame):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "button-group")
        self.layout_ = QtWidgets.QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(0)

    def addButton(self, button: Button) -> None:
        self.layout_.addWidget(button)


class InputGroup(QtWidgets.QFrame):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "input-group")
        self.layout_ = QtWidgets.QHBoxLayout(self)
        self.layout_.setContentsMargins(8, 0, 8, 0)
        self.layout_.setSpacing(6)
        self.prefixLabel = Label("", self, variant="muted")
        self.input = Input(self)
        self.suffixLabel = Label("", self, variant="muted")
        self.layout_.addWidget(self.prefixLabel)
        self.layout_.addWidget(self.input, 1)
        self.layout_.addWidget(self.suffixLabel)

    def get_prefix(self) -> str:
        return self.prefixLabel.text()

    def set_prefix(self, value: str) -> None:
        self.prefixLabel.setText(value)
        self.prefixLabel.setVisible(bool(value))

    def get_suffix(self) -> str:
        return self.suffixLabel.text()

    def set_suffix(self, value: str) -> None:
        self.suffixLabel.setText(value)
        self.suffixLabel.setVisible(bool(value))

    getPrefix = get_prefix
    setPrefix = set_prefix
    getSuffix = get_suffix
    setSuffix = set_suffix
    prefix = _qt.qt_property(str, fget=get_prefix, fset=set_prefix)
    suffix = _qt.qt_property(str, fget=get_suffix, fset=set_suffix)


class InputOTP(QtWidgets.QFrame):
    textChanged = _qt.qt_signal(str)
    complete = _qt.qt_signal(str)

    def __init__(self, parent: Optional[Any] = None, *, length: int = 6) -> None:
        super().__init__(parent)
        initialize_component(self, "input-otp")
        self._length = 0
        self._edits = []
        self._updating = False
        self.layout_ = QtWidgets.QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(6)
        self.set_code_length(length)

    def code_length(self) -> int:
        return self._length

    def set_code_length(self, length: int) -> None:
        length = int(length)
        if not 1 <= length <= 12:
            raise ValueError("codeLength must be between 1 and 12")
        while self._edits:
            edit = self._edits.pop()
            self.layout_.removeWidget(edit)
            edit.deleteLater()
        self._length = length
        for index in range(length):
            edit = Input(self)
            edit.setMaxLength(1)
            edit.setAlignment(_align_center())
            edit.setFixedWidth(38)
            edit.textChanged.connect(
                lambda text, position=index: self._slot_changed(position, text)
            )
            self._edits.append(edit)
            self.layout_.addWidget(edit)

    def text(self) -> str:
        return "".join(edit.text() for edit in self._edits)

    def setText(self, text: str) -> None:
        self._updating = True
        try:
            for index, edit in enumerate(self._edits):
                edit.setText(text[index] if index < len(text) else "")
        finally:
            self._updating = False
        self.textChanged.emit(self.text())

    def clear(self) -> None:
        self.setText("")
        if self._edits:
            self._edits[0].setFocus()

    def _slot_changed(self, index: int, text: str) -> None:
        if self._updating:
            return
        if text and index + 1 < len(self._edits):
            self._edits[index + 1].setFocus()
            self._edits[index + 1].selectAll()
        value = self.text()
        self.textChanged.emit(value)
        if len(value) == self._length:
            self.complete.emit(value)

    getCodeLength = code_length
    setCodeLength = set_code_length
    getValue = text
    setValue = setText
    codeLength = _qt.qt_property(int, fget=code_length, fset=set_code_length)
    value = _qt.qt_property(str, fget=text, fset=setText)


class Field(QtWidgets.QFrame):
    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        label: str = "Field",
        description: str = "",
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "field")
        self._required = False
        self.layout_ = QtWidgets.QVBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(6)
        self.labelWidget = Label(label, self, variant="small")
        self.controlContainer = QtWidgets.QWidget(self)
        self.controlLayout = QtWidgets.QVBoxLayout(self.controlContainer)
        self.controlLayout.setContentsMargins(0, 0, 0, 0)
        self.descriptionWidget = Label(description, self, variant="muted")
        self.errorWidget = Label("", self)
        self.errorWidget.setProperty("variant", "destructive")
        self.errorWidget.hide()
        self.layout_.addWidget(self.labelWidget)
        self.layout_.addWidget(self.controlContainer)
        self.layout_.addWidget(self.descriptionWidget)
        self.layout_.addWidget(self.errorWidget)

    def setControl(self, control: Any) -> None:
        while self.controlLayout.count():
            item = self.controlLayout.takeAt(0)
            if item.widget() is not None:
                item.widget().setParent(None)
        self.controlLayout.addWidget(control)

    def get_label(self) -> str:
        text = self.labelWidget.text()
        return text[:-2] if self._required and text.endswith(" *") else text

    def set_label(self, text: str) -> None:
        self.labelWidget.setText(text + (" *" if self._required else ""))

    def get_description(self) -> str:
        return self.descriptionWidget.text()

    def set_description(self, text: str) -> None:
        self.descriptionWidget.setText(text)
        self.descriptionWidget.setVisible(bool(text))

    def get_error(self) -> str:
        return self.errorWidget.text()

    def set_error(self, text: str) -> None:
        self.errorWidget.setText(text)
        self.errorWidget.setVisible(bool(text))
        self.setProperty("invalid", bool(text))
        refresh_style(self)

    def is_required(self) -> bool:
        return self._required

    def set_required(self, required: bool) -> None:
        label = self.get_label()
        self._required = bool(required)
        self.set_label(label)

    getLabel = get_label
    setLabel = set_label
    getLabelText = get_label
    setLabelText = set_label
    getDescription = get_description
    setDescription = set_description
    getError = get_error
    setError = set_error
    isRequired = is_required
    setRequired = set_required
    labelText = _qt.qt_property(str, fget=get_label, fset=set_label)
    description = _qt.qt_property(str, fget=get_description, fset=set_description)
    error = _qt.qt_property(str, fget=get_error, fset=set_error)
    required = _qt.qt_property(bool, fget=is_required, fset=set_required)


class RadioGroup(QtWidgets.QGroupBox):
    valueChanged = _qt.qt_signal(str)

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "radio-group")
        self.group = QtWidgets.QButtonGroup(self)
        self.layout_ = QtWidgets.QVBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self._buttons = {}

    def addOption(self, value: str, label: Optional[str] = None) -> RadioButton:
        button = RadioButton(label or value, self)
        button.toggled.connect(
            lambda checked, option=value: checked and self.valueChanged.emit(option)
        )
        self.group.addButton(button)
        self._buttons[value] = button
        self.layout_.addWidget(button)
        return button

    def value(self) -> str:
        for value, button in self._buttons.items():
            if button.isChecked():
                return value
        return ""

    def setValue(self, value: str) -> None:
        if value in self._buttons:
            self._buttons[value].setChecked(True)

    getSelectedValue = value
    setSelectedValue = setValue
    selectedValue = _qt.qt_property(str, fget=value, fset=setValue)


class Combobox(QtWidgets.QComboBox):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "combobox")
        self.setEditable(True)
        no_insert = getattr(QtWidgets.QComboBox, "NoInsert", None)
        if no_insert is None:
            no_insert = QtWidgets.QComboBox.InsertPolicy.NoInsert
        self.setInsertPolicy(no_insert)

    def setOptions(self, options: Iterable[str]) -> None:
        self.clear()
        self.addItems(list(options))


class NativeSelect(QtWidgets.QComboBox):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "native-select")


class DatePicker(QtWidgets.QDateEdit):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "date-picker")
        self.setCalendarPopup(True)
        self.setDate(QtCore.QDate.currentDate())


__all__ = [
    "ButtonGroup",
    "Combobox",
    "DatePicker",
    "Field",
    "InputGroup",
    "InputOTP",
    "NativeSelect",
    "RadioGroup",
    "Toggle",
    "ToggleGroup",
]
