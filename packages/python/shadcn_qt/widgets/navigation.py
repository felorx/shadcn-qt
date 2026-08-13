"""Navigation, command, and menu components."""

from __future__ import annotations

from typing import Any, Iterable, Optional, Sequence, Union

from shadcn_qt import _qt
from shadcn_qt.widgets._helpers import initialize_component
from shadcn_qt.widgets.button import Button
from shadcn_qt.widgets.controls import Label
from shadcn_qt.widgets.input import Input
from shadcn_qt.widgets._style import install_shadow

QtCore, _, QtWidgets = _qt.qt_modules()


class Breadcrumb(QtWidgets.QFrame):
    activated = _qt.qt_signal(str)

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        separator: str = "/",
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "breadcrumb")
        self._separator = separator
        self._items = []
        self.layout_ = QtWidgets.QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(6)
        self.layout_.addStretch(1)

    def setItems(self, items: Sequence[Union[str, tuple]]) -> None:
        while self.layout_.count() > 1:
            item = self.layout_.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        self._items = []
        for index, item in enumerate(items):
            if isinstance(item, tuple):
                label, value = str(item[0]), str(item[1])
            else:
                label = value = str(item)
            button = Button(label, self, variant="link", size="sm")
            button.clicked.connect(
                lambda checked=False, key=value: self.activated.emit(key)
            )
            self.layout_.insertWidget(self.layout_.count() - 1, button)
            self._items.append((label, value))
            if index + 1 < len(items):
                self.layout_.insertWidget(
                    self.layout_.count() - 1,
                    Label(self._separator, self, variant="muted"),
                )

    def get_separator(self) -> str:
        return self._separator

    def set_separator(self, separator: str) -> None:
        self._separator = separator
        if self._items:
            self.setItems(self._items)

    getSeparator = get_separator
    setSeparator = set_separator
    separator = _qt.qt_property(str, fget=get_separator, fset=set_separator)


class Pagination(QtWidgets.QFrame):
    pageChanged = _qt.qt_signal(int)

    def __init__(
        self,
        parent: Optional[Any] = None,
        *,
        page: int = 1,
        page_count: int = 1,
    ) -> None:
        super().__init__(parent)
        initialize_component(self, "pagination")
        self._page = 1
        self._requested_page = 1
        self._page_count = 1
        self.layout_ = QtWidgets.QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(4)
        self.previousButton = Button("Previous", self, variant="outline", size="sm")
        self.pageLabel = Label("1 / 1", self, variant="small")
        self.nextButton = Button("Next", self, variant="outline", size="sm")
        self.layout_.addStretch(1)
        self.layout_.addWidget(self.previousButton)
        self.layout_.addWidget(self.pageLabel)
        self.layout_.addWidget(self.nextButton)
        self.layout_.addStretch(1)
        self.previousButton.clicked.connect(self.previous)
        self.nextButton.clicked.connect(self.next)
        self.set_page_count(page_count)
        self.set_page(page)

    def page(self) -> int:
        return self._page

    def set_page(self, page: int) -> None:
        self._requested_page = max(1, int(page))
        page = min(self._requested_page, self._page_count)
        changed = page != self._page
        self._page = page
        self._sync()
        if changed:
            self.pageChanged.emit(page)

    def page_count(self) -> int:
        return self._page_count

    def set_page_count(self, count: int) -> None:
        previous = self._page
        self._page_count = max(1, int(count))
        self._page = min(self._requested_page, self._page_count)
        self._sync()
        if self._page != previous:
            self.pageChanged.emit(self._page)

    def next(self) -> None:
        self.set_page(self._page + 1)

    def previous(self) -> None:
        self.set_page(self._page - 1)

    def _sync(self) -> None:
        self.pageLabel.setText(f"{self._page} / {self._page_count}")
        self.previousButton.setEnabled(self._page > 1)
        self.nextButton.setEnabled(self._page < self._page_count)

    getPage = page
    setPage = set_page
    getCurrentPage = page
    setCurrentPage = set_page
    getPageCount = page_count
    setPageCount = set_page_count
    currentPage = _qt.qt_property(int, fget=page, fset=set_page)
    pageCount = _qt.qt_property(int, fget=page_count, fset=set_page_count)


class Command(QtWidgets.QFrame):
    selected = _qt.qt_signal(str)

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "command")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        self.search = Input(self)
        self.search.setPlaceholderText("Type a command or search…")
        self.list = QtWidgets.QListWidget(self)
        layout.addWidget(self.search)
        layout.addWidget(self.list, 1)
        self.search.textChanged.connect(self._filter)
        self.list.itemActivated.connect(
            lambda item: self.selected.emit(item.data(32) or item.text())
        )
        install_shadow(self, "md")

    def setItems(self, items: Iterable[Union[str, tuple]]) -> None:
        self.list.clear()
        for entry in items:
            if isinstance(entry, tuple):
                label, value = str(entry[0]), str(entry[1])
            else:
                label = value = str(entry)
            item = QtWidgets.QListWidgetItem(label)
            item.setData(32, value)
            self.list.addItem(item)

    def _filter(self, text: str) -> None:
        query = text.casefold()
        for index in range(self.list.count()):
            item = self.list.item(index)
            item.setHidden(query not in item.text().casefold())


class DropdownMenu(QtWidgets.QMenu):
    def __init__(
        self,
        title: Union[str, Any] = "Menu",
        parent: Optional[Any] = None,
    ) -> None:
        if isinstance(title, QtWidgets.QWidget) and parent is None:
            parent, title = title, "Menu"
        super().__init__(str(title), parent)
        initialize_component(self, "dropdown-menu")
        install_shadow(self, "md")

    def addItem(self, text: str, callback: Optional[Any] = None) -> Any:
        action = self.addAction(text)
        if callback is not None:
            action.triggered.connect(callback)
        return action


class ContextMenu(DropdownMenu):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__("Context menu", parent)
        self.setProperty("shadcn_qt_component", "context-menu")

    def attachTo(self, widget: Any) -> None:
        policy = getattr(QtCore.Qt, "CustomContextMenu", None)
        if policy is None:
            policy = QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        widget.setContextMenuPolicy(policy)
        widget.customContextMenuRequested.connect(
            lambda point: self._execute(widget.mapToGlobal(point))
        )

    def _execute(self, point: Any) -> None:
        execute = getattr(self, "exec", None) or getattr(self, "exec_", None)
        if not callable(execute):
            raise AttributeError("QMenu has neither exec nor exec_")
        execute(point)


class Menubar(QtWidgets.QMenuBar):
    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "menubar")
        install_shadow(self, "xs")


class NavigationMenu(QtWidgets.QFrame):
    activated = _qt.qt_signal(str)

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        initialize_component(self, "navigation-menu")
        self.layout_ = QtWidgets.QHBoxLayout(self)
        self.layout_.setContentsMargins(0, 0, 0, 0)
        self.layout_.setSpacing(4)
        self.layout_.addStretch(1)

    def addItem(self, text: str, value: Optional[str] = None) -> Button:
        button = Button(text, self, variant="ghost", size="sm")
        button.clicked.connect(
            lambda checked=False, key=value or text: self.activated.emit(key)
        )
        self.layout_.insertWidget(self.layout_.count() - 1, button)
        return button


__all__ = [
    "Breadcrumb",
    "Command",
    "ContextMenu",
    "DropdownMenu",
    "Menubar",
    "NavigationMenu",
    "Pagination",
]
