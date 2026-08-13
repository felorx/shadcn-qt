"""Container and layout-oriented shadcn components."""

from __future__ import annotations

from typing import Any, Optional

from shadcn_qt import _qt
from shadcn_qt.widgets._helpers import initialize_component, refresh_style
from shadcn_qt.widgets.button import Button

QtCore, _, QtWidgets = _qt.qt_modules()


def _orientation(name: str) -> Any:
    legacy = getattr(QtCore.Qt, name, None)
    return legacy if legacy is not None else getattr(QtCore.Qt.Orientation, name)


def _horizontal_expanding(widget: Any) -> None:
    expanding = getattr(QtWidgets.QSizePolicy, "Expanding", None)
    if expanding is None:
        expanding = QtWidgets.QSizePolicy.Policy.Expanding
    policy = widget.sizePolicy()
    policy.setHorizontalPolicy(expanding)
    widget.setSizePolicy(policy)


class AspectRatio(QtWidgets.QFrame):
    """A container that reports a height derived from its width."""

    def __init__(self, parent: Optional[Any] = None, *, ratio: float = 16 / 9) -> None:
        super().__init__(parent)
        initialize_component(self, "aspect-ratio")
        self._ratio = 16 / 9
        policy = self.sizePolicy()
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        self.set_ratio(ratio)

    def get_ratio(self) -> float:
        return self._ratio

    def set_ratio(self, ratio: float) -> None:
        ratio = float(ratio)
        if ratio <= 0:
            raise ValueError("ratio must be greater than zero")
        self._ratio = ratio
        self.updateGeometry()

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width: int) -> int:
        return max(1, round(width / self._ratio))

    getRatio = get_ratio
    setRatio = set_ratio
    ratio = _qt.qt_property(float, fget=get_ratio, fset=set_ratio)


class ScrollArea(QtWidgets.QScrollArea):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "scroll-area")
        self.setWidgetResizable(True)
        no_frame = getattr(QtWidgets.QFrame, "NoFrame", None)
        if no_frame is None:
            no_frame = QtWidgets.QFrame.Shape.NoFrame
        self.setFrameShape(no_frame)


class Resizable(QtWidgets.QSplitter):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(_orientation("Horizontal"), parent)
        initialize_component(self, "resizable")
        self.setChildrenCollapsible(False)


class Direction(QtWidgets.QFrame):
    """A container that applies left-to-right or right-to-left direction."""

    DIRECTIONS = ("ltr", "rtl")

    def __init__(self, parent: Optional[Any] = None, *, direction: str = "ltr") -> None:
        super().__init__(parent)
        initialize_component(self, "direction")
        self._direction = "ltr"
        self.content_layout = QtWidgets.QVBoxLayout(self)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.set_direction(direction)

    def addWidget(self, widget: Any) -> None:
        self.content_layout.addWidget(widget)

    def get_direction(self) -> str:
        return self._direction

    def set_direction(self, direction: str) -> None:
        if direction not in self.DIRECTIONS:
            raise ValueError(f"direction must be one of {self.DIRECTIONS}")
        self._direction = direction
        enum_name = "RightToLeft" if direction == "rtl" else "LeftToRight"
        layout_direction = getattr(QtCore.Qt, enum_name, None)
        if layout_direction is None:
            layout_direction = getattr(QtCore.Qt.LayoutDirection, enum_name)
        self.setLayoutDirection(layout_direction)
        refresh_style(self)

    getDirection = get_direction
    setDirection = set_direction
    direction = _qt.qt_property(str, fget=get_direction, fset=set_direction)


class Collapsible(QtWidgets.QFrame):
    expandedChanged = _qt.qt_signal(bool)

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        title: str = "Collapsible",
        expanded: bool = True,
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "collapsible")
        self._expanded = True
        self._title = title
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.trigger = Button("", self, variant="ghost", size="sm")
        _horizontal_expanding(self.trigger)
        self.trigger.setCheckable(True)
        self.trigger.clicked.connect(self.set_expanded)
        self.content = QtWidgets.QWidget(self)
        self.content_layout = QtWidgets.QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(12, 8, 12, 12)
        self.content_layout.setSpacing(8)
        self._layout.addWidget(self.trigger)
        self._layout.addWidget(self.content)
        self.set_expanded(expanded)

    def addWidget(self, widget: Any) -> None:
        if isinstance(widget, Button):
            _horizontal_expanding(widget)
        self.content_layout.addWidget(widget)

    def get_title(self) -> str:
        return self._title

    def set_title(self, title: str) -> None:
        self._title = title
        self._sync_trigger()

    def _sync_trigger(self) -> None:
        indicator = "▴" if self._expanded else "▾"
        self.trigger.setText(f"{self._title}  {indicator}")

    def is_expanded(self) -> bool:
        return self._expanded

    def set_expanded(self, expanded: bool) -> None:
        expanded = bool(expanded)
        changed = expanded != self._expanded
        self._expanded = expanded
        self.trigger.setChecked(expanded)
        self._sync_trigger()
        self.content.setVisible(expanded)
        refresh_style(self)
        if changed:
            self.expandedChanged.emit(expanded)

    getTitle = get_title
    setTitle = set_title
    isExpanded = is_expanded
    setExpanded = set_expanded
    title = _qt.qt_property(str, fget=get_title, fset=set_title)
    expanded = _qt.qt_property(bool, fget=is_expanded, fset=set_expanded)


class Accordion(QtWidgets.QFrame):
    currentChanged = _qt.qt_signal(int)

    def __init__(self, parent: Optional[Any] = None, *, exclusive: bool = True) -> None:
        super().__init__(parent)
        initialize_component(self, "accordion")
        self._exclusive = bool(exclusive)
        self._items = []
        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(1)
        self._layout.addStretch(1)

    def addItem(self, widget: Any, title: str) -> Collapsible:
        item = Collapsible(self, title=title, expanded=not self._items)
        item.addWidget(widget)
        item.expandedChanged.connect(
            lambda expanded, current=item: self._item_toggled(current, expanded)
        )
        self._items.append(item)
        self._layout.insertWidget(self._layout.count() - 1, item)
        return item

    def count(self) -> int:
        return len(self._items)

    def widget(self, index: int) -> Optional[Collapsible]:
        return self._items[index] if 0 <= index < len(self._items) else None

    def currentIndex(self) -> int:
        for index, item in enumerate(self._items):
            if item.expanded:
                return index
        return -1

    def setCurrentIndex(self, index: int) -> None:
        if not 0 <= index < len(self._items):
            return
        for item_index, item in enumerate(self._items):
            item.set_expanded(item_index == index if self._exclusive else item.expanded)
        if not self._exclusive:
            self._items[index].set_expanded(True)

    def is_exclusive(self) -> bool:
        return self._exclusive

    def set_exclusive(self, exclusive: bool) -> None:
        self._exclusive = bool(exclusive)
        if self._exclusive and self.currentIndex() >= 0:
            self.setCurrentIndex(self.currentIndex())

    def _item_toggled(self, current: Collapsible, expanded: bool) -> None:
        if expanded and self._exclusive:
            for item in self._items:
                if item is not current:
                    item.set_expanded(False)
        if expanded:
            self.currentChanged.emit(self._items.index(current))

    isExclusive = is_exclusive
    setExclusive = set_exclusive
    exclusive = _qt.qt_property(bool, fget=is_exclusive, fset=set_exclusive)


class Carousel(QtWidgets.QFrame):
    currentChanged = _qt.qt_signal(int)

    def __init__(self, parent: Optional[Any] = None, *, wrap: bool = True) -> None:
        super().__init__(parent)
        initialize_component(self, "carousel")
        self._wrap = bool(wrap)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        self.previousButton = Button("‹", self, variant="outline", size="icon")
        self.stack = QtWidgets.QStackedWidget(self)
        self.nextButton = Button("›", self, variant="outline", size="icon")
        layout.addWidget(self.previousButton)
        layout.addWidget(self.stack, 1)
        layout.addWidget(self.nextButton)
        self.previousButton.clicked.connect(self.previous)
        self.nextButton.clicked.connect(self.next)
        self.stack.currentChanged.connect(self.currentChanged)

    def addWidget(self, widget: Any) -> int:
        return self.stack.addWidget(widget)

    def count(self) -> int:
        return self.stack.count()

    def currentIndex(self) -> int:
        return self.stack.currentIndex()

    def setCurrentIndex(self, index: int) -> None:
        if self.count():
            self.stack.setCurrentIndex(max(0, min(index, self.count() - 1)))

    def next(self) -> None:
        if not self.count():
            return
        index = self.currentIndex() + 1
        self.setCurrentIndex(index % self.count() if self._wrap else index)

    def previous(self) -> None:
        if not self.count():
            return
        index = self.currentIndex() - 1
        self.setCurrentIndex(index % self.count() if self._wrap else index)

    def get_wrap(self) -> bool:
        return self._wrap

    def set_wrap(self, wrap: bool) -> None:
        self._wrap = bool(wrap)

    getWrap = get_wrap
    setWrap = set_wrap
    wrap = _qt.qt_property(bool, fget=get_wrap, fset=set_wrap)


class Sidebar(QtWidgets.QFrame):
    collapsedChanged = _qt.qt_signal(bool)
    SIDES = ("left", "right")

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        side: str = "left",
        collapsed: bool = False,
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "sidebar")
        self._side = "left"
        self._collapsed = False
        self._expanded_width = 256
        self.content_layout = QtWidgets.QVBoxLayout(self)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(6)
        self.set_side(side)
        self.set_collapsed(collapsed)

    def addWidget(self, widget: Any) -> None:
        if isinstance(widget, Button):
            _horizontal_expanding(widget)
        self.content_layout.addWidget(widget)

    def get_side(self) -> str:
        return self._side

    def set_side(self, side: str) -> None:
        if side not in self.SIDES:
            raise ValueError(f"side must be one of {self.SIDES}")
        self._side = side
        refresh_style(self)

    def is_collapsed(self) -> bool:
        return self._collapsed

    def set_collapsed(self, collapsed: bool) -> None:
        collapsed = bool(collapsed)
        changed = collapsed != self._collapsed
        self._collapsed = collapsed
        self.setMaximumWidth(56 if collapsed else 16777215)
        self.setMinimumWidth(56 if collapsed else min(160, self._expanded_width))
        refresh_style(self)
        if changed:
            self.collapsedChanged.emit(collapsed)

    getSide = get_side
    setSide = set_side
    isCollapsed = is_collapsed
    setCollapsed = set_collapsed
    side = _qt.qt_property(str, fget=get_side, fset=set_side)
    collapsed = _qt.qt_property(bool, fget=is_collapsed, fset=set_collapsed)


__all__ = [
    "Accordion",
    "AspectRatio",
    "Carousel",
    "Collapsible",
    "Direction",
    "Resizable",
    "ScrollArea",
    "Sidebar",
]
