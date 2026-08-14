"""Dialog, popup, tooltip, and toast components."""

from __future__ import annotations

from typing import Any, Optional, Union

from shadcn_qt import _qt
from shadcn_qt.widgets._helpers import initialize_component, refresh_style
from shadcn_qt.widgets._style import (
    animate_window_opacity,
    enable_antialiasing,
    install_shadow,
    semantic_color,
    with_alpha,
)
from shadcn_qt.widgets.button import Button
from shadcn_qt.widgets.controls import Label

QtCore, QtGui, QtWidgets = _qt.qt_modules()


def _window_flag(name: str) -> Any:
    value = getattr(QtCore.Qt, name, None)
    return value if value is not None else getattr(QtCore.Qt.WindowType, name)


class _CloseButton(Button):
    def __init__(self, parent: Any, *, size: int) -> None:
        super().__init__("", parent, variant="ghost", size="icon")
        self.setFixedSize(size, size)
        self.setAccessibleName("Close")

    def _icon_path(self) -> Any:
        center = QtCore.QRectF(self.rect()).center()
        path = QtGui.QPainterPath()
        path.moveTo(center.x() - 3.5, center.y() - 3.5)
        path.lineTo(center.x() + 3.5, center.y() + 3.5)
        path.moveTo(center.x() + 3.5, center.y() - 3.5)
        path.lineTo(center.x() - 3.5, center.y() + 3.5)
        return path

    def paintEvent(self, event: Any) -> None:
        super().paintEvent(event)
        painter = QtGui.QPainter(self)
        enable_antialiasing(painter)
        color = semantic_color(self, "foreground")
        if not self.isEnabled():
            color = with_alpha(color, 128)
        pen = QtGui.QPen(color, 1.5)
        cap = getattr(QtCore.Qt, "RoundCap", None)
        if cap is None:
            cap = QtCore.Qt.PenCapStyle.RoundCap
        pen.setCapStyle(cap)
        painter.setPen(pen)
        painter.drawPath(self._icon_path())


class _DialogOverlay(QtWidgets.QWidget):
    def __init__(self, parent: Any) -> None:
        super().__init__(parent)
        initialize_component(self, "dialog-overlay")
        self._opacity = QtWidgets.QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self.hide()

    def fadeIn(self) -> None:
        self._opacity.setOpacity(0.0)
        self.show()
        animation = QtCore.QPropertyAnimation(self._opacity, b"opacity", self)
        animation.setDuration(200)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.start()
        self._animation = animation


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
        self.setWindowFlag(_window_flag("FramelessWindowHint"), True)
        self.setModal(True)
        self.setMinimumWidth(360)
        self.setWindowTitle(title)
        self._overlay = _DialogOverlay(parent) if parent is not None else None
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
        self.footerLayout.setSpacing(8)
        self.footerLayout.addStretch(1)
        self.layout_.addWidget(self.titleLabel)
        self.layout_.addWidget(self.descriptionLabel)
        self.layout_.addWidget(self.content, 1)
        self.layout_.addWidget(self.footer)
        self.closeButton = _CloseButton(self, size=32)
        self.closeButton.setProperty("dialogRole", "close")
        self.closeButton.clicked.connect(self.reject)
        install_shadow(self, "lg")

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

    def resizeEvent(self, event: Any) -> None:
        self.closeButton.move(self.width() - self.closeButton.width() - 8, 8)
        self.closeButton.raise_()
        super().resizeEvent(event)

    def showEvent(self, event: Any) -> None:
        if self._overlay is not None:
            self._overlay.setGeometry(self.parentWidget().rect())
            self._overlay.fadeIn()
            self._overlay.raise_()
        super().showEvent(event)
        self.raise_()
        animate_window_opacity(self, duration=200)

    def hideEvent(self, event: Any) -> None:
        if self._overlay is not None:
            self._overlay.hide()
        super().hideEvent(event)

    def closeEvent(self, event: Any) -> None:
        if self._overlay is not None:
            self._overlay.hide()
        super().closeEvent(event)

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
        self.closeButton.hide()
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
        self.setModal(True)
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
        end_geometry = None
        if parent is not None:
            origin = parent.mapToGlobal(QtCore.QPoint(0, 0))
            width_available = parent.width()
            height_available = parent.height()
            if self._side in {"left", "right"}:
                width = min(420, max(280, round(width_available * 0.38)))
                self.resize(width, height_available)
                x = (
                    origin.x()
                    if self._side == "left"
                    else origin.x() + width_available - width
                )
                self.move(x, origin.y())
            else:
                height = min(360, max(200, round(height_available * 0.4)))
                self.resize(width_available, height)
                y = (
                    origin.y()
                    if self._side == "top"
                    else origin.y() + height_available - height
                )
                self.move(origin.x(), y)
            end_geometry = self.geometry()
        super().showEvent(event)
        if end_geometry is not None:
            start_geometry = QtCore.QRect(end_geometry)
            if self._side == "left":
                start_geometry.translate(-end_geometry.width(), 0)
            elif self._side == "right":
                start_geometry.translate(end_geometry.width(), 0)
            elif self._side == "top":
                start_geometry.translate(0, -end_geometry.height())
            else:
                start_geometry.translate(0, end_geometry.height())
            self.setGeometry(start_geometry)
            animation = QtCore.QPropertyAnimation(self, b"geometry", self)
            animation.setDuration(300)
            animation.setStartValue(start_geometry)
            animation.setEndValue(end_geometry)
            easing = getattr(QtCore.QEasingCurve, "OutCubic", None)
            if easing is None:
                easing = QtCore.QEasingCurve.Type.OutCubic
            animation.setEasingCurve(easing)
            animation.start()
            self._slide_animation = animation

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
        self.setMinimumWidth(288)
        self.contentLayout = QtWidgets.QVBoxLayout(self)
        self.contentLayout.setContentsMargins(16, 16, 16, 16)
        self.contentLayout.setSpacing(8)
        install_shadow(self, "md")

    def addWidget(self, widget: Any) -> None:
        self.contentLayout.addWidget(widget)

    def showAt(self, anchor: Any) -> None:
        point = anchor.mapToGlobal(QtCore.QPoint(0, anchor.height() + 6))
        self.adjustSize()
        self.move(point)
        self.show()
        self.raise_()
        animate_window_opacity(self, duration=150)


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
        self.setMargin(0)
        install_shadow(self, "sm")

    def showFor(self, widget: Any, duration: int = 2500) -> None:
        self.adjustSize()
        self.move(widget.mapToGlobal(QtCore.QPoint(0, widget.height() + 4)))
        self.show()
        animate_window_opacity(self, duration=120)
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
        self._closing = False
        self.setMinimumWidth(320)
        self.setMaximumWidth(420)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(14, 12, 10, 12)
        content = QtWidgets.QWidget(self)
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.titleLabel = Label(title, content, variant="small")
        self.descriptionLabel = Label(description, content, variant="muted")
        content_layout.addWidget(self.titleLabel)
        content_layout.addWidget(self.descriptionLabel)
        self.closeButton = _CloseButton(self, size=36)
        self.closeButton.clicked.connect(self.closeToast)
        layout.addWidget(content, 1)
        layout.addWidget(self.closeButton)
        self.set_variant(variant)
        install_shadow(self, "md")

    def showToast(self) -> None:
        self._closing = False
        self.adjustSize()
        target_height = max(56, self.sizeHint().height())
        self.setMaximumHeight(0)
        self.show()
        animation = QtCore.QPropertyAnimation(self, b"maximumHeight", self)
        animation.setDuration(180)
        animation.setStartValue(0)
        animation.setEndValue(target_height)
        animation.finished.connect(lambda: self.setMaximumHeight(16777215))
        animation.start()
        self._height_animation = animation
        if self._duration > 0:
            QtCore.QTimer.singleShot(self._duration, self.closeToast)

    def closeToast(self) -> None:
        if self._closing:
            return
        self._closing = True
        start_height = max(1, self.height())
        animation = QtCore.QPropertyAnimation(self, b"maximumHeight", self)
        animation.setDuration(150)
        animation.setStartValue(start_height)
        animation.setEndValue(0)

        def finish() -> None:
            self.hide()
            self.closed.emit()

        animation.finished.connect(finish)
        animation.start()
        self._height_animation = animation

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
