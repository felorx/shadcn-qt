"""Dialog, popup, tooltip, and toast components."""

from __future__ import annotations

from typing import Any, Optional, Union

from shadcn_qt import _qt
from shadcn_qt.widgets._helpers import initialize_component, refresh_style
from shadcn_qt.widgets.button import Button
from shadcn_qt.widgets.controls import Label

QtCore, _, QtWidgets = _qt.qt_modules()


def _window_flag(name: str) -> Any:
    value = getattr(QtCore.Qt, name, None)
    return value if value is not None else getattr(QtCore.Qt.WindowType, name)


class Dialog(QtWidgets.QDialog):
    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        title: str = "Dialog",
        description: str = "",
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "dialog")
        self.setModal(True)
        self.setMinimumWidth(360)
        self.layout_ = QtWidgets.QVBoxLayout(self)
        self.layout_.setContentsMargins(24, 24, 24, 24)
        self.layout_.setSpacing(12)
        self.titleLabel = Label(title, self, variant="large")
        self.descriptionLabel = Label(description, self, variant="muted")
        self.descriptionLabel.setWordWrap(True)
        self.content = QtWidgets.QWidget(self)
        self.contentLayout = QtWidgets.QVBoxLayout(self.content)
        self.contentLayout.setContentsMargins(0, 4, 0, 4)
        self.footer = QtWidgets.QWidget(self)
        self.footerLayout = QtWidgets.QHBoxLayout(self.footer)
        self.footerLayout.setContentsMargins(0, 0, 0, 0)
        self.footerLayout.addStretch(1)
        self.layout_.addWidget(self.titleLabel)
        self.layout_.addWidget(self.descriptionLabel)
        self.layout_.addWidget(self.content, 1)
        self.layout_.addWidget(self.footer)

    def addWidget(self, widget: Any) -> None:
        self.contentLayout.addWidget(widget)

    def addAction(self, button: Button) -> None:
        self.footerLayout.addWidget(button)

    def get_title(self) -> str:
        return self.titleLabel.text()

    def set_title(self, title: str) -> None:
        self.titleLabel.setText(title)
        self.setWindowTitle(title)

    def get_description(self) -> str:
        return self.descriptionLabel.text()

    def set_description(self, description: str) -> None:
        self.descriptionLabel.setText(description)
        self.descriptionLabel.setVisible(bool(description))

    def open(self) -> None:
        show = getattr(super(), "open", None)
        if callable(show):
            show()
        else:
            self.show()

    getTitle = get_title
    setTitle = set_title
    getDescription = get_description
    setDescription = set_description
    title = _qt.qt_property(str, fget=get_title, fset=set_title)
    description = _qt.qt_property(str, fget=get_description, fset=set_description)


class AlertDialog(Dialog):
    confirmed = _qt.qt_signal()
    cancelled = _qt.qt_signal()

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        title: str = "Are you sure?",
        description: str = "This action cannot be undone.",
    ) -> None:
        super().__init__(parent, title=title, description=description)
        self.setProperty("shadcn_qt_component", "alert-dialog")
        self.cancelButton = Button("Cancel", self, variant="outline")
        self.confirmButton = Button("Continue", self, variant="destructive")
        self.addAction(self.cancelButton)
        self.addAction(self.confirmButton)
        self.cancelButton.clicked.connect(self._cancel)
        self.confirmButton.clicked.connect(self._confirm)

    def _cancel(self) -> None:
        self.cancelled.emit()
        self.reject()

    def _confirm(self) -> None:
        self.confirmed.emit()
        self.accept()


class Sheet(Dialog):
    SIDES = ("left", "right", "top", "bottom")

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        side: str = "right",
        title: str = "Sheet",
        description: str = "",
    ) -> None:
        super().__init__(parent, title=title, description=description)
        self.setProperty("shadcn_qt_component", "sheet")
        self.setModal(False)
        self._side = "right"
        self.set_side(side)

    def get_side(self) -> str:
        return self._side

    def set_side(self, side: str) -> None:
        if side not in self.SIDES:
            raise ValueError(f"side must be one of {self.SIDES}")
        self._side = side
        refresh_style(self)

    def showEvent(self, event: Any) -> None:
        parent = self.parentWidget()
        if parent is not None:
            bounds = parent.frameGeometry()
            if self._side in {"left", "right"}:
                width = min(420, max(280, round(bounds.width() * 0.38)))
                self.resize(width, bounds.height())
                x = (
                    bounds.left()
                    if self._side == "left"
                    else bounds.right() - width + 1
                )
                self.move(x, bounds.top())
            else:
                height = min(360, max(200, round(bounds.height() * 0.4)))
                self.resize(bounds.width(), height)
                y = (
                    bounds.top()
                    if self._side == "top"
                    else bounds.bottom() - height + 1
                )
                self.move(bounds.left(), y)
        super().showEvent(event)

    getSide = get_side
    setSide = set_side
    side = _qt.qt_property(str, fget=get_side, fset=set_side)


class Drawer(Sheet):
    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        title: str = "Drawer",
        description: str = "",
    ) -> None:
        super().__init__(parent, side="bottom", title=title, description=description)
        self.setProperty("shadcn_qt_component", "drawer")


class Popover(QtWidgets.QFrame):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent, _window_flag("Popup"))
        initialize_component(self, "popover")
        self.setMinimumWidth(220)
        self.contentLayout = QtWidgets.QVBoxLayout(self)
        self.contentLayout.setContentsMargins(12, 12, 12, 12)
        self.contentLayout.setSpacing(8)

    def addWidget(self, widget: Any) -> None:
        self.contentLayout.addWidget(widget)

    def showAt(self, anchor: Any) -> None:
        point = anchor.mapToGlobal(QtCore.QPoint(0, anchor.height() + 6))
        self.adjustSize()
        self.move(point)
        self.show()
        self.raise_()


class HoverCard(Popover):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        self.setProperty("shadcn_qt_component", "hover-card")
        self._anchor = None

    def attachTo(self, widget: Any) -> None:
        if self._anchor is not None:
            self._anchor.removeEventFilter(self)
        self._anchor = widget
        widget.installEventFilter(self)

    def eventFilter(self, watched: Any, event: Any) -> bool:
        enter = getattr(QtCore.QEvent, "Enter", None)
        leave = getattr(QtCore.QEvent, "Leave", None)
        if enter is None:
            enter = QtCore.QEvent.Type.Enter
            leave = QtCore.QEvent.Type.Leave
        if watched is self._anchor and event.type() == enter:
            self.showAt(watched)
        elif watched is self._anchor and event.type() == leave:
            QtCore.QTimer.singleShot(120, self.hide)
        return False


class Tooltip(QtWidgets.QLabel):
    def __init__(
        self,
        text: Union[str, Any] = "Tooltip",
        parent: Optional[Any] = None,
    ) -> None:
        if isinstance(text, QtWidgets.QWidget) and parent is None:
            parent, text = text, "Tooltip"
        super().__init__(str(text), parent, _window_flag("ToolTip"))
        initialize_component(self, "tooltip")
        self.setMargin(6)

    def showFor(self, widget: Any, duration: int = 2500) -> None:
        self.adjustSize()
        self.move(widget.mapToGlobal(QtCore.QPoint(0, widget.height() + 4)))
        self.show()
        QtCore.QTimer.singleShot(duration, self.hide)

    def attachTo(self, widget: Any) -> None:
        widget.setToolTip(self.text())


class Toast(QtWidgets.QFrame):
    closed = _qt.qt_signal()
    VARIANTS = ("default", "success", "destructive", "warning")

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        title: str = "Notification",
        description: str = "",
        variant: str = "default",
        duration: int = 4000,
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "toast")
        self._variant = "default"
        self._duration = int(duration)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 10, 12)
        content = QtWidgets.QWidget(self)
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.titleLabel = Label(title, content, variant="small")
        self.descriptionLabel = Label(description, content, variant="muted")
        content_layout.addWidget(self.titleLabel)
        content_layout.addWidget(self.descriptionLabel)
        self.closeButton = Button("×", self, variant="ghost", size="icon")
        self.closeButton.clicked.connect(self.closeToast)
        layout.addWidget(content, 1)
        layout.addWidget(self.closeButton)
        self.set_variant(variant)

    def showToast(self) -> None:
        self.show()
        if self._duration > 0:
            QtCore.QTimer.singleShot(self._duration, self.closeToast)

    def closeToast(self) -> None:
        self.hide()
        self.closed.emit()

    def get_variant(self) -> str:
        return self._variant

    def set_variant(self, variant: str) -> None:
        if variant not in self.VARIANTS:
            raise ValueError(f"variant must be one of {self.VARIANTS}")
        self._variant = variant
        refresh_style(self)

    def duration(self) -> int:
        return self._duration

    def setDuration(self, duration: int) -> None:
        self._duration = max(0, int(duration))

    getVariant = get_variant
    setVariant = set_variant
    getDurationMs = duration
    setDurationMs = setDuration
    variant = _qt.qt_property(str, fget=get_variant, fset=set_variant)
    durationMs = _qt.qt_property(int, fget=duration, fset=setDuration)


class Sonner(QtWidgets.QFrame):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "sonner")
        self.layout_ = QtWidgets.QVBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(8)
        self.layout_.addStretch(1)

    def toast(
        self,
        title: str,
        description: str = "",
        *,
        variant: str = "default",
        duration: int = 4000,
    ) -> Toast:
        toast = Toast(
            self,
            title=title,
            description=description,
            variant=variant,
            duration=duration,
        )
        self.layout_.insertWidget(self.layout_.count() - 1, toast)
        toast.closed.connect(toast.deleteLater)
        toast.showToast()
        return toast


__all__ = [
    "AlertDialog",
    "Dialog",
    "Drawer",
    "HoverCard",
    "Popover",
    "Sheet",
    "Sonner",
    "Toast",
    "Tooltip",
]
