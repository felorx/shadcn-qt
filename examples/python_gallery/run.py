#!/usr/bin/env python3
"""Browse and interact with every public shadcn-qt Core component."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

from shadcn_qt import (
    BASE_COLOR,
    STYLE_PROFILE,
    __version__,
    app_exec,
    apply_theme,
    enable_native_widget_styling,
)
from shadcn_qt import widgets as ui
from shadcn_qt._qt import QtCore, QtGui, QtWidgets
from shadcn_qt.widgets._icons import _paint_vector_icon

COMPONENT_CATEGORIES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "Actions and forms",
        (
            "Button",
            "ButtonGroup",
            "Toggle",
            "ToggleGroup",
            "Input",
            "InputGroup",
            "InputOTP",
            "TextArea",
            "Checkbox",
            "RadioButton",
            "RadioGroup",
            "Switch",
            "Select",
            "NativeSelect",
            "Combobox",
            "DatePicker",
            "Slider",
            "Field",
            "Label",
        ),
    ),
    (
        "Layout and disclosure",
        (
            "Accordion",
            "AspectRatio",
            "Card",
            "Carousel",
            "Collapsible",
            "Direction",
            "Resizable",
            "ScrollArea",
            "Separator",
            "Sidebar",
            "TabPane",
            "Tabs",
        ),
    ),
    (
        "Dialogs and feedback",
        (
            "Alert",
            "AlertDialog",
            "Dialog",
            "Drawer",
            "HoverCard",
            "Popover",
            "Sheet",
            "Sonner",
            "Toast",
            "Tooltip",
        ),
    ),
    (
        "Navigation and menus",
        (
            "Breadcrumb",
            "Command",
            "ContextMenu",
            "DropdownMenu",
            "Menubar",
            "NavigationMenu",
            "Pagination",
        ),
    ),
    (
        "Data and content",
        (
            "Avatar",
            "Badge",
            "Calendar",
            "Chart",
            "DataTable",
            "Empty",
            "Item",
            "Kbd",
            "Progress",
            "Skeleton",
            "Spinner",
            "Table",
            "Typography",
        ),
    ),
    (
        "Conversation",
        ("Attachment", "Bubble", "Marker", "Message", "MessageScroller"),
    ),
)

NATIVE_OVERVIEW_NAMES: Tuple[str, ...] = (
    "Native Forms",
    "Native Data Views",
    "Native Containers",
    "Native Window Chrome",
)

NATIVE_FORM_NAMES: Tuple[str, ...] = (
    "QLabel",
    "QPushButton",
    "QCommandLinkButton",
    "QToolButton",
    "QCheckBox",
    "QRadioButton",
    "QLineEdit",
    "QPlainTextEdit",
    "QTextEdit",
    "QTextBrowser",
    "QKeySequenceEdit",
    "QSpinBox",
    "QDoubleSpinBox",
    "QDateEdit",
    "QTimeEdit",
    "QDateTimeEdit",
    "QComboBox",
    "QFontComboBox",
    "QSlider",
    "QDial",
    "QScrollBar",
    "QProgressBar",
    "QDialogButtonBox",
    "QLCDNumber",
)

NATIVE_DATA_VIEW_NAMES: Tuple[str, ...] = (
    "QListView",
    "QListWidget",
    "QTreeView",
    "QTreeWidget",
    "QTableView",
    "QTableWidget",
    "QColumnView",
    "QHeaderView",
    "QCalendarWidget",
    "QUndoView",
)

NATIVE_CONTAINER_NAMES: Tuple[str, ...] = (
    "QWidget",
    "QFrame",
    "QGroupBox",
    "QTabWidget",
    "QTabBar",
    "QToolBox",
    "QStackedWidget",
    "QScrollArea",
    "QSplitter",
    "QSplitterHandle",
    "QMdiArea",
    "QMdiSubWindow",
    "QGraphicsView",
    "QFocusFrame",
    "QSizeGrip",
    "QRubberBand",
    *(("QDesktopWidget",) if hasattr(QtWidgets, "QDesktopWidget") else ()),
    *(("QRhiWidget",) if hasattr(QtWidgets, "QRhiWidget") else ()),
)

NATIVE_WINDOW_NAMES: Tuple[str, ...] = (
    "QMenuBar",
    "QMenu",
    "QToolBar",
    "QStatusBar",
    "QDockWidget",
    "QDialog",
    "QMainWindow",
    "QWizard",
    "QWizardPage",
    "QSplashScreen",
)

NATIVE_DIALOG_NAMES: Tuple[str, ...] = (
    "QMessageBox",
    "QFileDialog",
    "QColorDialog",
    "QFontDialog",
    "QInputDialog",
    "QProgressDialog",
    "QErrorMessage",
)

NATIVE_WIDGET_CATEGORIES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "Native QtWidgets",
        NATIVE_OVERVIEW_NAMES,
    ),
    ("Native Forms", NATIVE_FORM_NAMES),
    ("Native Data Views", NATIVE_DATA_VIEW_NAMES),
    ("Native Containers", NATIVE_CONTAINER_NAMES),
    ("Native Windows", NATIVE_WINDOW_NAMES),
    ("Native Dialogs", NATIVE_DIALOG_NAMES),
)

CATEGORY_DESCRIPTIONS: Dict[str, str] = {
    "Actions and forms": "Inputs, selections, validation states, and actions.",
    "Layout and disclosure": "Qt-native containers and progressive disclosure.",
    "Dialogs and feedback": "Alerts, popups, overlays, and transient feedback.",
    "Navigation and menus": "Navigation structures, commands, menus, and paging.",
    "Data and content": "Structured data, status, visualization, and typography.",
    "Conversation": "Attachments, message bubbles, markers, and chat scrolling.",
    "Native QtWidgets": (
        "Composite views of stock QtWidgets adopted by the reversible adapter."
    ),
    "Native Forms": "One stock Qt form control per preview page.",
    "Native Data Views": "One Qt model/view control per preview page.",
    "Native Containers": "One Qt container family per preview page.",
    "Native Windows": "One native window surface per preview page.",
    "Native Dialogs": "One embedded stock Qt dialog per preview page.",
}

GALLERY_QSS = """
QTreeWidget#galleryNavigation { outline: none; }
QTreeWidget#galleryNavigation::item { min-height: 26px; padding: 3px 6px; }
QWidget#galleryPreviewHost { min-height: 420px; }
QFrame#galleryPreviewCard { min-width: 560px; }
QLabel[nativePreviewHeading="true"] { font-size: 14px; font-weight: 600; }
"""


class _GalleryNavigationTree(QtWidgets.QTreeWidget):
    """Tree with theme-aware vector disclosure indicators for category rows."""

    EXPANSION_MODES = ("single-click", "double-click")

    def __init__(self, parent: Optional[Any] = None) -> None:
        super().__init__(parent)
        self._expansion_mode = "single-click"
        # Category expansion is handled for the whole row below, including the
        # disclosure indicator, so the platform default must stay disabled.
        self.setExpandsOnDoubleClick(False)

    def get_expansion_mode(self) -> str:
        return self._expansion_mode

    def set_expansion_mode(self, mode: str) -> None:
        if mode not in self.EXPANSION_MODES:
            raise ValueError(
                f"expansion mode must be one of {self.EXPANSION_MODES}, got {mode!r}"
            )
        self._expansion_mode = mode

    getExpansionMode = get_expansion_mode
    setExpansionMode = set_expansion_mode

    def _item_at_event(self, event: Any) -> Any:
        position = getattr(event, "position", None)
        point = position() if callable(position) else event.pos()
        to_point = getattr(point, "toPoint", None)
        return self.itemAt(to_point() if callable(to_point) else point)

    @staticmethod
    def _is_category(item: Any) -> bool:
        return item is not None and item.parent() is None and item.childCount() > 0

    @staticmethod
    def _is_left_click(event: Any) -> bool:
        left_button = getattr(QtCore.Qt, "LeftButton", None)
        if left_button is None:
            left_button = QtCore.Qt.MouseButton.LeftButton
        return event.button() == left_button

    def branch_icon_name(self, index: Any) -> str:
        return "chevron-down" if self.isExpanded(index) else "chevron-right"

    def drawBranches(self, painter: Any, rect: Any, index: Any) -> None:
        if index.parent().isValid() or not self.model().hasChildren(index):
            return
        indicator_size = min(self.indentation(), rect.height())
        indicator_rect = QtCore.QRectF(
            rect.right() - indicator_size + 1,
            rect.top(),
            indicator_size,
            rect.height(),
        )
        painter.save()
        _paint_vector_icon(
            self,
            painter,
            self.branch_icon_name(index),
            rect=indicator_rect,
            color_name="mutedForeground",
        )
        painter.restore()

    def mousePressEvent(self, event: Any) -> None:
        item = self._item_at_event(event)
        if self._is_left_click(event) and self._is_category(item):
            self.setCurrentItem(item)
            if self._expansion_mode == "single-click":
                item.setExpanded(not item.isExpanded())
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: Any) -> None:
        item = self._item_at_event(event)
        if self._is_left_click(event) and self._is_category(item):
            if self._expansion_mode == "double-click":
                item.setExpanded(not item.isExpanded())
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


def component_names() -> Tuple[str, ...]:
    """Return every component presented by the gallery."""

    return tuple(
        name for _category, components in COMPONENT_CATEGORIES for name in components
    )


def component_category(name: str) -> str:
    for category, components in COMPONENT_CATEGORIES:
        if name in components:
            return category
    raise KeyError(name)


def native_preview_names() -> Tuple[str, ...]:
    return tuple(
        name
        for _category, previews in NATIVE_WIDGET_CATEGORIES
        for name in previews
    )


def native_overview_names() -> Tuple[str, ...]:
    return NATIVE_OVERVIEW_NAMES


def native_individual_preview_names() -> Tuple[str, ...]:
    return (
        NATIVE_FORM_NAMES
        + NATIVE_DATA_VIEW_NAMES
        + NATIVE_CONTAINER_NAMES
        + NATIVE_WINDOW_NAMES
        + NATIVE_DIALOG_NAMES
    )


def gallery_names() -> Tuple[str, ...]:
    return component_names() + native_preview_names()


def gallery_category(name: str) -> str:
    try:
        return component_category(name)
    except KeyError:
        for category, previews in NATIVE_WIDGET_CATEGORIES:
            if name in previews:
                return category
    raise KeyError(name)


def _user_role() -> Any:
    value = getattr(QtCore.Qt, "UserRole", None)
    return value if value is not None else QtCore.Qt.ItemDataRole.UserRole


def _align_center() -> Any:
    value = getattr(QtCore.Qt, "AlignCenter", None)
    return value if value is not None else QtCore.Qt.AlignmentFlag.AlignCenter


def _clear_layout(layout: Any) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.hide()
            widget.deleteLater()
        elif child_layout is not None:
            _clear_layout(child_layout)


def _preview_host(parent: Any) -> Tuple[Any, Any]:
    host = QtWidgets.QWidget(parent)
    host.setObjectName("galleryPreviewHost")
    layout = QtWidgets.QVBoxLayout(host)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(14)
    host._gallery_objects = []
    return host, layout


def _row(layout: Any) -> Tuple[Any, Any]:
    row = QtWidgets.QWidget()
    row_layout = QtWidgets.QHBoxLayout(row)
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_layout.setSpacing(10)
    layout.addWidget(row)
    return row, row_layout


def _store(host: Any, *objects: Any) -> None:
    host._gallery_objects.extend(objects)


def _label(text: str, parent: Any, *, variant: str = "muted") -> Any:
    label = ui.Label(text, parent, variant=variant)
    label.setWordWrap(True)
    return label


def _card_with_text(parent: Any, title: str, description: str) -> Any:
    card = ui.Card(parent)
    layout = QtWidgets.QVBoxLayout(card)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(6)
    layout.addWidget(ui.Label(title, card, variant="large"))
    layout.addWidget(_label(description, card))
    return card


def _menu_popup(menu: Any, button: Any) -> None:
    show_at = getattr(menu, "showAt", None)
    if callable(show_at):
        show_at(button)
    else:
        point = button.mapToGlobal(QtCore.QPoint(0, button.height()))
        menu.popup(point)


def build_component_preview(name: str, parent: Any = None) -> Any:
    """Build an interactive preview for one public component."""

    if name not in component_names():
        raise KeyError(f"Unknown gallery component: {name}")

    host, layout = _preview_host(parent)

    if name == "Button":
        variants = ("default", "secondary", "outline", "ghost", "destructive", "link")
        _, buttons = _row(layout)
        for variant in variants:
            buttons.addWidget(ui.Button(variant.title(), host, variant=variant))
        buttons.addStretch(1)
        _, sizes = _row(layout)
        for size in ("sm", "default", "lg", "icon"):
            sizes.addWidget(ui.Button("+" if size == "icon" else size, host, size=size))
        sizes.addStretch(1)

    elif name == "ButtonGroup":
        group = ui.ButtonGroup(host)
        group.addButton(ui.Button("Day", group, variant="outline"))
        group.addButton(ui.Button("Week", group, variant="outline"))
        group.addButton(ui.Button("Month", group, variant="outline"))
        layout.addWidget(group)

    elif name == "Toggle":
        _, row = _row(layout)
        bold = ui.Toggle("Bold", host, variant="outline")
        bold.setChecked(True)
        row.addWidget(bold)
        row.addWidget(ui.Toggle("Italic", host))
        row.addStretch(1)

    elif name == "ToggleGroup":
        group = ui.ToggleGroup(host)
        group.addItem("left", "Left")
        group.addItem("center", "Center")
        group.addItem("right", "Right")
        group.setValue("center")
        layout.addWidget(group)

    elif name == "Input":
        normal = ui.Input(host)
        normal.setPlaceholderText("name@example.com")
        invalid = ui.Input(host)
        invalid.setText("invalid address")
        invalid.set_invalid(True)
        layout.addWidget(normal)
        layout.addWidget(invalid)
        layout.addWidget(
            _label("The second input demonstrates the invalid state.", host)
        )

    elif name == "InputGroup":
        group = ui.InputGroup(host)
        group.set_prefix("$")
        group.set_suffix("USD")
        group.input.setPlaceholderText("0.00")
        layout.addWidget(group)

    elif name == "InputOTP":
        otp = ui.InputOTP(host, length=6)
        otp.setText("248")
        layout.addWidget(otp)
        layout.addWidget(
            _label("Continue typing to complete the six-digit code.", host)
        )

    elif name == "TextArea":
        area = ui.TextArea(host)
        area.setPlaceholderText("Write a short message…")
        area.setPlainText("shadcn-qt keeps the native QPlainTextEdit API.")
        area.setMinimumHeight(130)
        layout.addWidget(area)

    elif name == "Checkbox":
        _, row = _row(layout)
        checked = ui.Checkbox("Accept notifications", host)
        checked.setChecked(True)
        row.addWidget(checked)
        row.addWidget(ui.Checkbox("Disabled option", host))
        row.itemAt(1).widget().setEnabled(False)
        row.addStretch(1)

    elif name == "RadioButton":
        _, row = _row(layout)
        group = QtWidgets.QButtonGroup(host)
        for index, text in enumerate(("Email", "SMS", "Push")):
            button = ui.RadioButton(text, host)
            button.setChecked(index == 0)
            group.addButton(button)
            row.addWidget(button)
        row.addStretch(1)
        _store(host, group)

    elif name == "RadioGroup":
        group = ui.RadioGroup(host)
        group.addOption("starter", "Starter")
        group.addOption("team", "Team")
        group.addOption("enterprise", "Enterprise")
        group.setValue("team")
        layout.addWidget(group)

    elif name == "Switch":
        switch = ui.Switch("Use dark appearance", host)
        switch.setChecked(True)
        layout.addWidget(switch)

    elif name in {"Select", "NativeSelect"}:
        select = getattr(ui, name)(host)
        select.addItems(["PySide6", "PyQt6", "PySide2", "PyQt5"])
        select.setCurrentText("PySide6")
        layout.addWidget(select)

    elif name == "Combobox":
        combo = ui.Combobox(host)
        combo.setOptions(["New York", "London", "Shanghai", "Tokyo"])
        combo.setCurrentText("Shanghai")
        layout.addWidget(combo)

    elif name == "DatePicker":
        layout.addWidget(ui.DatePicker(host))

    elif name == "Slider":
        slider = ui.Slider(host)
        slider.setRange(0, 100)
        slider.setValue(64)
        layout.addWidget(slider)
        layout.addWidget(_label("Current value: 64", host))

    elif name == "Field":
        field = ui.Field(
            host, label="Email", description="Used for account notifications."
        )
        control = ui.Input(field)
        control.setText("not-an-email")
        field.setControl(control)
        field.set_required(True)
        field.set_error("Enter a valid email address.")
        layout.addWidget(field)

    elif name == "Label":
        for variant in ("large", "lead", "default", "small", "muted", "destructive"):
            layout.addWidget(
                ui.Label(f"{variant.title()} label", host, variant=variant)
            )

    elif name == "Accordion":
        accordion = ui.Accordion(host)
        accordion.addItem(
            _label("Native widgets, familiar signals, Qt layouts.", accordion),
            "Why Qt?",
        )
        accordion.addItem(
            _label("One token source generates Python and C++ themes.", accordion),
            "How are themes built?",
        )
        accordion.addItem(
            _label("PySide6, PyQt6, PySide2, and PyQt5.", accordion),
            "Which bindings work?",
        )
        layout.addWidget(accordion)

    elif name == "AspectRatio":
        ratio = ui.AspectRatio(host, ratio=16 / 9)
        ratio.setObjectName("galleryAspectRatioDemo")
        ratio.setMaximumWidth(520)
        ratio.setMinimumWidth(360)
        ratio_layout = QtWidgets.QVBoxLayout(ratio)
        ratio_layout.setContentsMargins(0, 0, 0, 0)
        ratio_layout.setAlignment(_align_center())
        surface = ui.Card(ratio)
        surface_layout = QtWidgets.QVBoxLayout(surface)
        surface_layout.setContentsMargins(24, 24, 24, 24)
        surface_layout.setSpacing(6)
        surface_layout.addStretch(1)
        surface_layout.addWidget(
            ui.Label("16:9", surface, variant="large"), 0, _align_center()
        )
        surface_layout.addWidget(
            ui.Label(
                "Responsive preview surface · 520 × 293",
                surface,
                variant="muted",
            ),
            0,
            _align_center(),
        )
        surface_layout.addStretch(1)
        ratio_layout.addWidget(surface)
        layout.addWidget(ratio)

    elif name == "Card":
        layout.addWidget(
            _card_with_text(
                host,
                "Project activity",
                "Classic new-york surface with rounded-xl geometry and shadow.",
            )
        )

    elif name == "Carousel":
        carousel = ui.Carousel(host)
        carousel.setMinimumHeight(180)
        for index in range(1, 4):
            card = _card_with_text(
                carousel, f"Slide {index}", "Use the arrow buttons to navigate."
            )
            carousel.addWidget(card)
        layout.addWidget(carousel)

    elif name == "Collapsible":
        collapsible = ui.Collapsible(host, title="Account details", expanded=True)
        collapsible.addWidget(
            _label("Email: ada@example.com", collapsible, variant="default")
        )
        collapsible.addWidget(
            _label("Role: Administrator", collapsible, variant="default")
        )
        layout.addWidget(collapsible)

    elif name == "Direction":
        direction = ui.Direction(host, direction="rtl")
        direction.addWidget(
            ui.Label("واجهة من اليمين إلى اليسار", direction, variant="large")
        )
        direction.addWidget(ui.Input(direction))
        direction.content_layout.itemAt(1).widget().setPlaceholderText("اكتب هنا")
        layout.addWidget(direction)

    elif name == "Resizable":
        splitter = ui.Resizable(host)
        splitter.setMinimumHeight(220)
        splitter.addWidget(
            _card_with_text(
                splitter, "Navigation", "Drag the handle to resize this pane."
            )
        )
        splitter.addWidget(
            _card_with_text(splitter, "Content", "QSplitter behavior is preserved.")
        )
        splitter.setSizes([220, 420])
        layout.addWidget(splitter)

    elif name == "ScrollArea":
        area = ui.ScrollArea(host)
        area.setMinimumHeight(250)
        content = QtWidgets.QWidget(area)
        content_layout = QtWidgets.QVBoxLayout(content)
        for index in range(1, 13):
            content_layout.addWidget(
                ui.Item(
                    content,
                    title=f"Activity {index}",
                    description="Scrollable native content",
                )
            )
        area.setWidget(content)
        layout.addWidget(area)

    elif name == "Separator":
        layout.addWidget(ui.Label("Section one", host, variant="large"))
        layout.addWidget(ui.Separator(host))
        _, row = _row(layout)
        row.addWidget(ui.Label("Left", host))
        vertical = ui.Separator(host, orientation="vertical")
        vertical.setMinimumHeight(48)
        row.addWidget(vertical)
        row.addWidget(ui.Label("Right", host))
        row.addStretch(1)

    elif name == "Sidebar":
        _, row = _row(layout)
        sidebar = ui.Sidebar(host)
        sidebar.addWidget(ui.Label("Workspace", sidebar, variant="large"))
        sidebar.addWidget(ui.Button("Overview", sidebar, variant="secondary"))
        sidebar.addWidget(ui.Button("Projects", sidebar, variant="ghost"))
        sidebar.addWidget(ui.Button("Settings", sidebar, variant="ghost"))
        row.addWidget(sidebar)
        content = _card_with_text(
            host,
            "Dashboard",
            "The sidebar can collapse without replacing its layout API.",
        )
        row.addWidget(content, 1)
        toggle = ui.Button("Toggle sidebar", host, variant="outline")
        toggle.clicked.connect(
            lambda checked=False: sidebar.set_collapsed(not sidebar.is_collapsed())
        )
        layout.addWidget(toggle)

    elif name in {"Tabs", "TabPane"}:
        tabs = ui.Tabs(host) if name == "Tabs" else ui.TabPane(host)
        if name == "TabPane":
            tabs.setMovable(True)
            tabs.setTabsClosable(True)
            tabs.setDocumentMode(True)
        for title, copy in (
            ("Account", "Profile and email settings"),
            ("Security", "Passwords and sessions"),
            ("Billing", "Plan and invoices"),
            ("Activity", "Recent workspace activity"),
        ):
            if name == "TabPane":
                page = QtWidgets.QWidget(tabs)
                page_layout = QtWidgets.QVBoxLayout(page)
                page_layout.setContentsMargins(24, 24, 24, 24)
                page_layout.addWidget(_label(title, page, variant="large"))
                page_layout.addWidget(_label(copy, page))
                page_layout.addStretch(1)
            else:
                page = _card_with_text(tabs, title, copy)
            tabs.addTab(page, title)
        if name == "TabPane":
            def close_tab(index: int) -> None:
                page = tabs.widget(index)
                tabs.removeTab(index)
                if page is not None:
                    page.deleteLater()

            tabs.tabCloseRequested.connect(close_tab)
            tabs.setMinimumHeight(260)
            layout.addWidget(
                _label(
                    "Drag labels to reorder them or use the close buttons. "
                    "All standard QTabWidget signals and methods remain available.",
                    host,
                )
            )
        layout.addWidget(tabs)

    elif name == "Alert":
        for variant, title, copy in (
            ("default", "Heads up", "This is a standard informational alert."),
            ("destructive", "Action required", "Your session needs attention."),
        ):
            alert = ui.Alert(host, variant=variant)
            alert_layout = QtWidgets.QVBoxLayout(alert)
            alert_layout.setContentsMargins(16, 12, 16, 12)
            alert_layout.setSpacing(4)
            alert_layout.addWidget(ui.Label(title, alert, variant="small"))
            alert_layout.addWidget(_label(copy, alert))
            layout.addWidget(alert)

    elif name in {"Dialog", "AlertDialog", "Sheet", "Drawer"}:
        if name == "Dialog":
            overlay = ui.Dialog(
                host,
                title="Edit profile",
                description="Update your public account information.",
            )
            overlay.addWidget(ui.Input(overlay))
            overlay.contentLayout.itemAt(0).widget().setPlaceholderText("Display name")
            overlay.addAction(ui.Button("Save", overlay))
        elif name == "AlertDialog":
            overlay = ui.AlertDialog(
                host,
                title="Delete project?",
                description="This action cannot be undone.",
            )
        elif name == "Sheet":
            overlay = ui.Sheet(
                host,
                side="right",
                title="Project settings",
                description="A modal side panel with a dimmed overlay.",
            )
            overlay.addWidget(ui.Switch("Enable notifications", overlay))
        else:
            overlay = ui.Drawer(
                host, title="Command drawer", description="A bottom-aligned sheet."
            )
            overlay.addWidget(ui.Command(overlay))
            overlay.contentLayout.itemAt(0).widget().setItems(
                ["Create project", "Open settings", "View shortcuts"]
            )
        trigger = ui.Button(f"Open {name}", host)
        trigger.clicked.connect(overlay.open)
        layout.addWidget(trigger)
        layout.addWidget(
            _label("Click the button to exercise the real overlay behavior.", host)
        )
        _store(host, overlay)

    elif name == "Popover":
        trigger = ui.Button("Open popover", host, variant="outline")
        popover = ui.Popover(host)
        popover.addWidget(ui.Label("Dimensions", popover, variant="large"))
        popover.addWidget(ui.InputGroup(popover))
        popover.contentLayout.itemAt(1).widget().set_prefix("W")
        popover.contentLayout.itemAt(1).widget().set_suffix("px")
        trigger.clicked.connect(lambda checked=False: popover.showAt(trigger))
        layout.addWidget(trigger)
        _store(host, popover)

    elif name == "HoverCard":
        trigger = ui.Button("Hover over @shadcn-qt", host, variant="link")
        card = ui.HoverCard(host)
        card.addWidget(ui.Label("shadcn-qt", card, variant="large"))
        card.addWidget(
            _label("Qt-native components with shadcn-aligned semantics.", card)
        )
        card.attachTo(trigger)
        layout.addWidget(trigger)
        _store(host, card)

    elif name == "Sonner":
        sonner = ui.Sonner(host)
        sonner.setMinimumHeight(230)
        trigger = ui.Button("Add toast", host)
        trigger.clicked.connect(
            lambda checked=False: sonner.toast(
                "Saved",
                "Your changes are now available.",
                variant="success",
                duration=2500,
            )
        )
        layout.addWidget(trigger)
        layout.addWidget(sonner)

    elif name == "Toast":
        toast = ui.Toast(
            host,
            title="Deployment complete",
            description="Version 0.1.0 is live.",
            variant="success",
            duration=0,
        )
        layout.addWidget(toast)

    elif name == "Tooltip":
        trigger = ui.Button("Hover or click for help", host, variant="outline")
        tooltip = ui.Tooltip("This action creates a new project.", host)
        tooltip.attachTo(trigger)
        trigger.clicked.connect(lambda checked=False: tooltip.showFor(trigger))
        layout.addWidget(trigger)
        _store(host, tooltip)

    elif name == "Breadcrumb":
        breadcrumb = ui.Breadcrumb(host)
        breadcrumb.setItems(
            [
                ("Home", "home"),
                ("Components", "components"),
                ("Breadcrumb", "breadcrumb"),
            ]
        )
        layout.addWidget(breadcrumb)

    elif name == "Command":
        command = ui.Command(host)
        command.setItems(
            [
                ("Open file", "open"),
                ("Save all", "save"),
                ("Toggle theme", "theme"),
                ("Show shortcuts", "shortcuts"),
            ]
        )
        command.setMinimumHeight(260)
        layout.addWidget(command)

    elif name == "ContextMenu":
        target = _card_with_text(
            host,
            "Right-click this card",
            "The context menu uses the native Qt custom-context-menu policy.",
        )
        menu = ui.ContextMenu(host)
        menu.addItem("Back")
        menu.addItem("Reload")
        menu.addSeparator()
        menu.addItem("Inspect")
        menu.attachTo(target)
        layout.addWidget(target)
        _store(host, menu)

    elif name == "DropdownMenu":
        trigger = ui.Button("Open menu", host, variant="outline")
        menu = ui.DropdownMenu("Account", host)
        menu.addItem("Profile")
        menu.addItem("Billing")
        menu.addSeparator()
        menu.addItem("Sign out")
        trigger.clicked.connect(lambda checked=False: _menu_popup(menu, trigger))
        layout.addWidget(trigger)
        _store(host, menu)

    elif name == "Menubar":
        menubar = ui.Menubar(host)
        file_menu = menubar.addMenu("File")
        file_menu.addAction("New window")
        file_menu.addAction("Open…")
        edit_menu = menubar.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        layout.addWidget(menubar)

    elif name == "NavigationMenu":
        menu = ui.NavigationMenu(host)
        menu.addItem("Overview")
        menu.addItem("Components")
        menu.addItem("Documentation")
        menu.addItem("GitHub")
        layout.addWidget(menu)

    elif name == "Pagination":
        layout.addWidget(ui.Pagination(host, page=3, page_count=8))

    elif name == "Avatar":
        _, row = _row(layout)
        for fallback, size in (("CN", 32), ("QT", 48), ("AI", 64)):
            row.addWidget(ui.Avatar(fallback, host, size=size))
        row.addStretch(1)

    elif name == "Badge":
        _, row = _row(layout)
        for variant in ("default", "secondary", "outline", "destructive"):
            row.addWidget(ui.Badge(variant.title(), host, variant=variant))
        row.addStretch(1)

    elif name == "Calendar":
        calendar = ui.Calendar(host)
        calendar.setMaximumWidth(440)
        layout.addWidget(calendar)

    elif name == "Chart":
        _, row = _row(layout)
        for chart_type in ("line", "bar"):
            chart = ui.Chart(
                host, chart_type=chart_type, values=[12, 28, 18, 42, 34, 50]
            )
            chart.setMinimumHeight(220)
            row.addWidget(chart, 1)

    elif name == "DataTable":
        table = ui.DataTable(host)
        table.setRows(
            ["Name", "Role", "Status"],
            [
                ["Ada", "Admin", "Active"],
                ["Lin", "Developer", "Active"],
                ["Sam", "Designer", "Invited"],
            ],
        )
        table.setMinimumHeight(240)
        layout.addWidget(table)

    elif name == "Empty":
        empty = ui.Empty(
            host,
            title="No projects",
            description="Create a project to start building your interface.",
        )
        empty.setAction(ui.Button("Create project", empty))
        empty.setMinimumHeight(260)
        layout.addWidget(empty)

    elif name == "Item":
        layout.addWidget(
            ui.Item(
                host, title="shadcn-qt 0.1.0", description="Public Core package · PyPI"
            )
        )
        layout.addWidget(
            ui.Item(
                host,
                title="Documentation",
                description="Installation, Designer, themes, and migration",
            )
        )

    elif name == "Kbd":
        _, row = _row(layout)
        row.addWidget(ui.Kbd("⌘", host))
        row.addWidget(ui.Kbd("K", host))
        row.addWidget(_label("Open command menu", host, variant="default"))
        row.addStretch(1)

    elif name == "Progress":
        progress = ui.Progress(host)
        progress.setRange(0, 100)
        progress.setValue(68)
        layout.addWidget(progress)
        layout.addWidget(_label("Uploading artifacts · 68%", host))

    elif name == "Skeleton":
        _, row = _row(layout)
        avatar = ui.Skeleton(host)
        avatar.setFixedSize(48, 48)
        row.addWidget(avatar)
        lines = QtWidgets.QWidget(host)
        lines_layout = QtWidgets.QVBoxLayout(lines)
        lines_layout.setContentsMargins(0, 0, 0, 0)
        for width in (280, 220, 150):
            skeleton = ui.Skeleton(lines)
            skeleton.setFixedSize(width, 16)
            lines_layout.addWidget(skeleton)
        row.addWidget(lines, 1)

    elif name == "Spinner":
        spinner = ui.Spinner(host)
        layout.addWidget(spinner)
        layout.addWidget(_label("Loading component metadata…", host))

    elif name == "Table":
        table = ui.Table(host)
        table.setColumnCount(3)
        table.setRowCount(3)
        table.setHorizontalHeaderLabels(["Package", "Version", "Channel"])
        rows = (
            ("shadcn-qt", "0.1.0", "PyPI"),
            ("PySide6", "6.11", "Qt"),
            ("Python", "3.9+", "Runtime"),
        )
        for row_index, values in enumerate(rows):
            for column_index, value in enumerate(values):
                table.setItem(
                    row_index, column_index, QtWidgets.QTableWidgetItem(value)
                )
        table.resizeColumnsToContents()
        table.setMinimumHeight(230)
        layout.addWidget(table)

    elif name == "Typography":
        samples = (
            ("h1", "Build native Qt interfaces"),
            ("h2", "Semantic components"),
            ("lead", "One API for PySide and PyQt."),
            (
                "p",
                "Components retain native signals, models, layouts, and "
                "accessibility behavior.",
            ),
            ("code", "python -m pip install shadcn-qt[pyside6]"),
            (
                "muted",
                "Independent and not affiliated with the upstream shadcn project.",
            ),
        )
        for level, text in samples:
            layout.addWidget(ui.Typography(text, host, level=level))

    elif name == "Attachment":
        attachment = ui.Attachment(
            host, name="component-gallery.png", detail="184 KB · PNG"
        )
        attachment.removed.connect(attachment.hide)
        layout.addWidget(attachment)

    elif name == "Bubble":
        left = ui.Bubble(
            "How do I install the Core package?",
            host,
            variant="secondary",
            alignment="start",
        )
        right = ui.Bubble(
            "Use one binding extra, for example shadcn-qt[pyside6].",
            host,
            alignment="end",
        )
        layout.addWidget(left)
        layout.addWidget(right)

    elif name == "Marker":
        _, row = _row(layout)
        for variant, text in (
            ("default", "New"),
            ("status", "Online"),
            ("separator", "Today"),
        ):
            row.addWidget(ui.Marker(text, host, variant=variant))
        row.addStretch(1)

    elif name == "Message":
        layout.addWidget(
            ui.Message(
                host,
                author="shadcn-qt",
                content="The complete Core catalog is available from PyPI.",
            )
        )

    elif name == "MessageScroller":
        scroller = ui.MessageScroller(host)
        scroller.setMinimumHeight(300)
        scroller.addMessage(
            ui.Message(
                scroller,
                author="Developer",
                content="Can I keep my existing PyQt5 application?",
            )
        )
        scroller.addMessage(
            ui.Message(
                scroller,
                author="shadcn-qt",
                content="Yes. Install the base package without a binding extra.",
            )
        )
        scroller.addMessage(
            ui.Message(
                scroller,
                author="Developer",
                content="Great — I can migrate one page at a time.",
            )
        )
        layout.addWidget(scroller)

    layout.addStretch(1)
    host.setProperty("gallery_component", name)
    return host


def _native_group(title: str, parent: Any) -> Tuple[Any, Any]:
    group = QtWidgets.QGroupBox(title, parent)
    layout = QtWidgets.QVBoxLayout(group)
    layout.setContentsMargins(14, 18, 14, 14)
    layout.setSpacing(10)
    return group, layout


def _native_heading(text: str, parent: Any) -> Any:
    label = QtWidgets.QLabel(text, parent)
    label.setProperty("nativePreviewHeading", True)
    return label


def _add_native_form_control(
    layout: Any, label: str, widget: Any, parent: Any
) -> None:
    widget.setProperty("nativeGalleryFormControl", True)
    layout.addWidget(_native_heading(label, parent))
    layout.addWidget(widget)


def _native_horizontal() -> Any:
    value = getattr(QtCore.Qt, "Horizontal", None)
    return value if value is not None else QtCore.Qt.Orientation.Horizontal


def _native_widget_flag() -> Any:
    value = getattr(QtCore.Qt, "Widget", None)
    return value if value is not None else QtCore.Qt.WindowType.Widget


def _native_standard_buttons(*names: str) -> Any:
    scope = getattr(QtWidgets.QDialogButtonBox, "StandardButton", None)
    result = None
    for name in names:
        value = getattr(QtWidgets.QDialogButtonBox, name, None)
        if value is None:
            value = getattr(scope, name)
        result = value if result is None else result | value
    return result


def _native_message_buttons(*names: str) -> Any:
    scope = getattr(QtWidgets.QMessageBox, "StandardButton", None)
    result = None
    for name in names:
        value = getattr(QtWidgets.QMessageBox, name, None)
        if value is None:
            value = getattr(scope, name)
        result = value if result is None else result | value
    return result


def _native_enum(owner: Any, name: str, group: str) -> Any:
    value = getattr(owner, name, None)
    return value if value is not None else getattr(getattr(owner, group), name)


def _native_form_specimen(name: str, parent: Any) -> Any:
    if name == "QLabel":
        widget = QtWidgets.QLabel(
            "QLabel keeps selection, word wrapping, and native text metrics.", parent
        )
        widget.setWordWrap(True)
    elif name == "QPushButton":
        widget = QtWidgets.QPushButton("Save changes", parent)
    elif name == "QCommandLinkButton":
        widget = QtWidgets.QCommandLinkButton(
            "Open workspace", "Continue with an existing project", parent
        )
    elif name == "QToolButton":
        widget = QtWidgets.QToolButton(parent)
        widget.setText("Tool action")
    elif name == "QCheckBox":
        widget = QtWidgets.QCheckBox("Enable notifications", parent)
        widget.setChecked(True)
    elif name == "QRadioButton":
        widget = QtWidgets.QRadioButton("Team plan", parent)
        widget.setChecked(True)
    elif name == "QLineEdit":
        widget = QtWidgets.QLineEdit(parent)
        widget.setPlaceholderText("name@example.com")
    elif name == "QPlainTextEdit":
        widget = QtWidgets.QPlainTextEdit(parent)
        widget.setPlainText("QPlainTextEdit preserves its QTextDocument API.")
        widget.setMinimumHeight(150)
    elif name == "QTextEdit":
        widget = QtWidgets.QTextEdit(parent)
        widget.setHtml("<b>QTextEdit</b><br>Rich text editing remains available.")
        widget.setMinimumHeight(150)
    elif name == "QTextBrowser":
        widget = QtWidgets.QTextBrowser(parent)
        widget.setHtml(
            "<h3>Native document</h3><p>Links, selection, and scrolling remain "
            "unchanged.</p>"
        )
        widget.setMinimumHeight(180)
    elif name == "QKeySequenceEdit":
        widget = QtWidgets.QKeySequenceEdit(parent)
        widget.setKeySequence(QtGui.QKeySequence("Ctrl+K"))
    elif name == "QSpinBox":
        widget = QtWidgets.QSpinBox(parent)
        widget.setRange(0, 100)
        widget.setValue(24)
    elif name == "QDoubleSpinBox":
        widget = QtWidgets.QDoubleSpinBox(parent)
        widget.setRange(0.0, 100.0)
        widget.setValue(12.5)
    elif name == "QDateEdit":
        widget = QtWidgets.QDateEdit(QtCore.QDate(2026, 8, 14), parent)
        widget.setCalendarPopup(True)
    elif name == "QTimeEdit":
        widget = QtWidgets.QTimeEdit(QtCore.QTime(9, 30), parent)
    elif name == "QDateTimeEdit":
        widget = QtWidgets.QDateTimeEdit(
            QtCore.QDateTime(QtCore.QDate(2026, 8, 14), QtCore.QTime(9, 30)),
            parent,
        )
        widget.setCalendarPopup(True)
    elif name == "QComboBox":
        widget = QtWidgets.QComboBox(parent)
        widget.addItems(["PySide6", "PyQt6", "PySide2", "PyQt5"])
    elif name == "QFontComboBox":
        widget = QtWidgets.QFontComboBox(parent)
    elif name == "QSlider":
        widget = QtWidgets.QSlider(_native_horizontal(), parent)
        widget.setValue(64)
    elif name == "QDial":
        widget = QtWidgets.QDial(parent)
        widget.setRange(0, 100)
        widget.setValue(64)
        widget.setNotchesVisible(True)
        widget.setFixedSize(140, 140)
    elif name == "QScrollBar":
        widget = QtWidgets.QScrollBar(_native_horizontal(), parent)
        widget.setRange(0, 100)
        widget.setValue(40)
    elif name == "QProgressBar":
        widget = QtWidgets.QProgressBar(parent)
        widget.setValue(64)
    elif name == "QDialogButtonBox":
        widget = QtWidgets.QDialogButtonBox(
            _native_standard_buttons("Cancel", "Save"), parent
        )
    elif name == "QLCDNumber":
        widget = QtWidgets.QLCDNumber(parent)
        widget.setDigitCount(6)
        widget.display(2026)
        widget.setMinimumHeight(100)
    else:
        raise KeyError(name)
    return widget


def _native_tree_model(parent: Any) -> Any:
    model = QtGui.QStandardItemModel(parent)
    model.setHorizontalHeaderLabels(["Workspace", "State"])
    project = QtGui.QStandardItem("shadcn-qt")
    project.appendRow([QtGui.QStandardItem("Python"), QtGui.QStandardItem("Ready")])
    project.appendRow([QtGui.QStandardItem("C++"), QtGui.QStandardItem("Planned")])
    model.appendRow([project, QtGui.QStandardItem("Active")])
    return model


def _native_table_model(parent: Any) -> Any:
    model = QtGui.QStandardItemModel(3, 3, parent)
    model.setHorizontalHeaderLabels(["Component", "Binding", "State"])
    for row, values in enumerate(
        (
            ("Button", "PySide6", "Ready"),
            ("Calendar", "PyQt6", "Ready"),
            ("Dialog", "Qt 5/6", "Ready"),
        )
    ):
        for column, value in enumerate(values):
            model.setItem(row, column, QtGui.QStandardItem(value))
    return model


def _native_data_specimen(name: str, parent: Any) -> Any:
    if name == "QListView":
        widget = QtWidgets.QListView(parent)
        model = QtGui.QStandardItemModel(widget)
        for text in ("Overview", "Activity", "Settings", "Billing"):
            model.appendRow(QtGui.QStandardItem(text))
        widget.setModel(model)
        widget.setCurrentIndex(model.index(1, 0))
    elif name == "QListWidget":
        widget = QtWidgets.QListWidget(parent)
        widget.addItems(["Overview", "Activity", "Settings", "Billing"])
        widget.setCurrentRow(1)
    elif name == "QTreeView":
        widget = QtWidgets.QTreeView(parent)
        model = _native_tree_model(widget)
        widget.setModel(model)
        widget.expandAll()
    elif name == "QTreeWidget":
        widget = QtWidgets.QTreeWidget(parent)
        widget.setHeaderLabels(["Workspace", "State"])
        project = QtWidgets.QTreeWidgetItem(["shadcn-qt", "Active"])
        project.addChild(QtWidgets.QTreeWidgetItem(["Python", "Ready"]))
        project.addChild(QtWidgets.QTreeWidgetItem(["C++", "Planned"]))
        widget.addTopLevelItem(project)
        project.setExpanded(True)
    elif name == "QTableView":
        widget = QtWidgets.QTableView(parent)
        widget.setModel(_native_table_model(widget))
        widget.horizontalHeader().setStretchLastSection(True)
    elif name == "QTableWidget":
        widget = QtWidgets.QTableWidget(3, 3, parent)
        widget.setHorizontalHeaderLabels(["Component", "Binding", "State"])
        for row, values in enumerate(
            (
                ("Button", "PySide6", "Ready"),
                ("Calendar", "PyQt6", "Ready"),
                ("Dialog", "Qt 5/6", "Ready"),
            )
        ):
            for column, value in enumerate(values):
                widget.setItem(row, column, QtWidgets.QTableWidgetItem(value))
        widget.horizontalHeader().setStretchLastSection(True)
    elif name == "QColumnView":
        widget = QtWidgets.QColumnView(parent)
        model = _native_tree_model(widget)
        widget.setModel(model)
        widget.setCurrentIndex(model.index(0, 0))
    elif name == "QHeaderView":
        widget = QtWidgets.QHeaderView(_native_horizontal(), parent)
        model = _native_table_model(widget)
        widget.setModel(model)
        widget.setStretchLastSection(True)
        widget.setFixedHeight(40)
    elif name == "QCalendarWidget":
        widget = QtWidgets.QCalendarWidget(parent)
        widget.setSelectedDate(QtCore.QDate(2026, 8, 14))
        widget.setMaximumWidth(520)
    elif name == "QUndoView":
        widget = QtWidgets.QUndoView(parent)
        stack_type = getattr(QtGui, "QUndoStack", None) or getattr(
            QtWidgets, "QUndoStack"
        )
        command_type = getattr(QtGui, "QUndoCommand", None) or getattr(
            QtWidgets, "QUndoCommand"
        )
        stack = stack_type(widget)
        for text in ("Create workspace", "Apply Zinc theme", "Add Gallery page"):
            stack.push(command_type(text))
        widget.setStack(stack)
        widget.setCurrentIndex(widget.model().index(1, 0))
    else:
        raise KeyError(name)
    if name != "QHeaderView":
        widget.setMinimumHeight(240)
    return widget


def _native_container_specimen(name: str, parent: Any) -> Any:
    if name == "QWidget":
        widget = QtWidgets.QWidget(parent)
        content = QtWidgets.QVBoxLayout(widget)
        content.addWidget(QtWidgets.QLabel("Base QWidget content", widget))
        content.addWidget(QtWidgets.QPushButton("Native child control", widget))
        content.addStretch(1)
        widget.setMinimumHeight(180)
    elif name == "QFrame":
        widget = QtWidgets.QFrame(parent)
        widget.setFrameShape(
            _native_enum(QtWidgets.QFrame, "StyledPanel", "Shape")
        )
        content = QtWidgets.QVBoxLayout(widget)
        content.addWidget(QtWidgets.QLabel("QFrame panel content", widget))
        content.addStretch(1)
        widget.setMinimumHeight(180)
    elif name == "QGroupBox":
        widget = QtWidgets.QGroupBox("Native group box", parent)
        content = QtWidgets.QVBoxLayout(widget)
        content.addWidget(QtWidgets.QCheckBox("Preserve signals", widget))
        content.addWidget(QtWidgets.QRadioButton("Use Qt models", widget))
        content.addStretch(1)
        widget.setMinimumHeight(180)
    elif name == "QTabWidget":
        widget = QtWidgets.QTabWidget(parent)
        widget.setDocumentMode(True)
        widget.setMovable(True)
        widget.setTabsClosable(True)
        for title in ("Account", "Security", "Billing", "Activity"):
            page = QtWidgets.QWidget(widget)
            page_layout = QtWidgets.QVBoxLayout(page)
            page_layout.addWidget(QtWidgets.QLabel(f"{title} settings", page))
            page_layout.addStretch(1)
            widget.addTab(page, title)
        widget.tabCloseRequested.connect(widget.removeTab)
        widget.setMinimumHeight(220)
    elif name == "QTabBar":
        widget = QtWidgets.QTabBar(parent)
        widget.setMovable(True)
        widget.setTabsClosable(True)
        for title in ("Account", "Security", "Billing", "Activity"):
            widget.addTab(title)
        widget.tabCloseRequested.connect(widget.removeTab)
    elif name == "QToolBox":
        widget = QtWidgets.QToolBox(parent)
        for title in ("Profile", "Notifications", "Advanced"):
            page = QtWidgets.QWidget(widget)
            page_layout = QtWidgets.QVBoxLayout(page)
            page_layout.addWidget(QtWidgets.QLabel(f"{title} settings", page))
            page_layout.addStretch(1)
            widget.addItem(page, title)
        widget.setMinimumHeight(240)
    elif name == "QStackedWidget":
        wrapper = QtWidgets.QWidget(parent)
        wrapper_layout = QtWidgets.QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        widget = QtWidgets.QStackedWidget(wrapper)
        for title in ("Account", "Security", "Billing"):
            widget.addWidget(QtWidgets.QLabel(f"{title} page", widget))
        widget.setCurrentIndex(1)
        wrapper_layout.addWidget(widget)
        wrapper.setMinimumHeight(180)
        return wrapper
    elif name == "QScrollArea":
        widget = QtWidgets.QScrollArea(parent)
        widget.setWidgetResizable(True)
        content = QtWidgets.QWidget(widget)
        content_layout = QtWidgets.QVBoxLayout(content)
        for index in range(1, 9):
            content_layout.addWidget(
                QtWidgets.QLabel(f"Scrollable row {index}", content)
            )
        content_layout.addStretch(1)
        widget.setWidget(content)
        widget.setMinimumHeight(240)
    elif name == "QSplitter":
        widget = QtWidgets.QSplitter(_native_horizontal(), parent)
        widget.addWidget(QtWidgets.QTextEdit("Left pane", widget))
        widget.addWidget(QtWidgets.QTextEdit("Right pane", widget))
        widget.setSizes([260, 420])
        widget.setMinimumHeight(220)
    elif name == "QSplitterHandle":
        widget = QtWidgets.QSplitter(_native_horizontal(), parent)
        widget.setHandleWidth(12)
        widget.addWidget(QtWidgets.QTextEdit("Drag the handle", widget))
        widget.addWidget(QtWidgets.QTextEdit("to resize panes", widget))
        widget.setSizes([320, 320])
        widget.setMinimumHeight(220)
    elif name in {"QMdiArea", "QMdiSubWindow"}:
        widget = QtWidgets.QMdiArea(parent)
        for index in range(1, 3 if name == "QMdiArea" else 2):
            subwindow = QtWidgets.QMdiSubWindow(widget)
            subwindow.setWindowTitle(f"Subwindow {index}")
            subwindow.setWidget(QtWidgets.QLabel("Native MDI content", subwindow))
            widget.addSubWindow(subwindow)
            subwindow.show()
        widget.setMinimumHeight(260)
    elif name == "QGraphicsView":
        widget = QtWidgets.QGraphicsView(parent)
        scene = QtWidgets.QGraphicsScene(widget)
        path = QtGui.QPainterPath()
        path.addRoundedRect(20, 20, 260, 110, 8, 8)
        scene.addPath(path)
        scene.addText("QGraphicsView scene")
        widget.setScene(scene)
        widget.setMinimumHeight(240)
    elif name == "QFocusFrame":
        wrapper = QtWidgets.QWidget(parent)
        wrapper.setMinimumHeight(160)
        content = QtWidgets.QVBoxLayout(wrapper)
        target = QtWidgets.QLineEdit(wrapper)
        target.setText("Focused control")
        content.addWidget(target)
        content.addStretch(1)
        focus = QtWidgets.QFocusFrame(wrapper)
        focus.setWidget(target)
        # QFocusFrame reparents itself to the target's window on Cocoa, while
        # the offscreen plugin keeps it below ``wrapper``. Preserve the actual
        # specimen explicitly instead of relying on platform-specific QObject
        # ancestry during preview validation.
        wrapper._native_gallery_target = focus
        target.setFocus()
        return wrapper
    elif name == "QSizeGrip":
        wrapper = QtWidgets.QWidget(parent)
        wrapper.setMinimumHeight(180)
        content = QtWidgets.QHBoxLayout(wrapper)
        content.addWidget(QtWidgets.QLabel("Resize handle", wrapper))
        content.addStretch(1)
        bottom = QtWidgets.QVBoxLayout()
        bottom.addStretch(1)
        bottom.addWidget(QtWidgets.QSizeGrip(wrapper))
        content.addLayout(bottom)
        return wrapper
    elif name == "QRubberBand":
        wrapper = QtWidgets.QWidget(parent)
        wrapper.setMinimumHeight(220)
        rubber = QtWidgets.QRubberBand(
            _native_enum(QtWidgets.QRubberBand, "Rectangle", "Shape"), wrapper
        )
        rubber.setGeometry(48, 48, 280, 110)
        rubber.show()
        return wrapper
    elif name == "QDesktopWidget" and hasattr(QtWidgets, "QDesktopWidget"):
        widget = QtWidgets.QDesktopWidget(parent)
        content = QtWidgets.QVBoxLayout(widget)
        geometry = widget.availableGeometry()
        content.addWidget(
            QtWidgets.QLabel(
                f"Available desktop: {geometry.width()} × {geometry.height()}",
                widget,
            )
        )
        content.addStretch(1)
        widget.setMinimumHeight(180)
    elif name == "QRhiWidget" and hasattr(QtWidgets, "QRhiWidget"):
        # Configure the backend before parenting into a visible Gallery. On
        # Cocoa, constructing directly below a visible parent can polish the
        # widget while its API is still Null and emit misleading "No QRhi"
        # diagnostics.
        widget = QtWidgets.QRhiWidget()
        platform_name = QtWidgets.QApplication.platformName().casefold()
        api_name = {
            "cocoa": "Metal",
            "windows": "Direct3D11",
            "xcb": "OpenGL",
            "wayland": "OpenGL",
        }.get(platform_name, "Null")
        api_scope = getattr(QtWidgets.QRhiWidget, "Api", QtWidgets.QRhiWidget)
        widget.setApi(getattr(api_scope, api_name))
        widget.setParent(parent)
        content = QtWidgets.QVBoxLayout(widget)
        content.addWidget(
            QtWidgets.QLabel(
                "QRhiWidget render surface · backend supplied by the host", widget
            )
        )
        content.addStretch(1)
        widget.setMinimumHeight(220)
    else:
        raise KeyError(name)
    return widget


def _native_window_specimen(name: str, parent: Any) -> Any:
    if name == "QMenuBar":
        widget = QtWidgets.QMenuBar(parent)
        widget.addMenu("File").addAction("New project")
        widget.addMenu("Edit").addAction("Preferences")
    elif name == "QMenu":
        widget = QtWidgets.QMenu("Workspace", parent)
        widget.setWindowFlags(_native_widget_flag())
        widget.addAction("New project")
        widget.addAction("Open workspace")
        widget.addSeparator()
        widget.addAction("Preferences")
        widget.setMinimumWidth(240)
    elif name == "QToolBar":
        widget = QtWidgets.QToolBar("Workspace", parent)
        widget.addAction("New")
        widget.addAction("Open")
        widget.addSeparator()
        widget.addAction("Save")
    elif name == "QStatusBar":
        widget = QtWidgets.QStatusBar(parent)
        widget.showMessage("Ready · native status message")
    elif name == "QDockWidget":
        widget = QtWidgets.QDockWidget("Inspector", parent)
        contents = QtWidgets.QListWidget(widget)
        contents.addItems(["Geometry", "Appearance", "Accessibility"])
        widget.setWidget(contents)
        widget.setMinimumHeight(220)
    elif name == "QDialog":
        widget = QtWidgets.QDialog(parent)
        widget.setWindowFlags(_native_widget_flag())
        content = QtWidgets.QVBoxLayout(widget)
        content.addWidget(QtWidgets.QLabel("Embedded QDialog", widget))
        content.addWidget(QtWidgets.QLineEdit(widget))
        content.addStretch(1)
        content.addWidget(
            QtWidgets.QDialogButtonBox(
                _native_standard_buttons("Cancel", "Ok"), widget
            )
        )
        widget.setMinimumHeight(220)
    elif name == "QMainWindow":
        widget = QtWidgets.QMainWindow(parent)
        widget.setWindowFlags(_native_widget_flag())
        widget.menuBar().addMenu("File").addAction("New project")
        toolbar = QtWidgets.QToolBar("Workspace", widget)
        toolbar.addAction("Save")
        widget.addToolBar(toolbar)
        widget.setCentralWidget(QtWidgets.QLabel("QMainWindow content", widget))
        widget.statusBar().showMessage("Ready")
        widget.setMinimumHeight(280)
    elif name == "QWizard":
        widget = QtWidgets.QWizard(parent)
        widget.setWindowFlags(_native_widget_flag())
        page = QtWidgets.QWizardPage(widget)
        page.setTitle("Create a workspace")
        page.setSubTitle("Wizard navigation remains native.")
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.addWidget(QtWidgets.QLineEdit(page))
        widget.addPage(page)
        widget.setMinimumHeight(300)
    elif name == "QWizardPage":
        widget = QtWidgets.QWizardPage(parent)
        widget.setTitle("Workspace details")
        widget.setSubTitle("A standalone QWizardPage specimen.")
        content = QtWidgets.QVBoxLayout(widget)
        content.addWidget(QtWidgets.QLabel("Page content", widget))
        content.addWidget(QtWidgets.QLineEdit(widget))
        content.addStretch(1)
        widget.setMinimumHeight(220)
    elif name == "QSplashScreen":
        pixmap = QtGui.QPixmap(640, 240)
        pixmap.fill(QtGui.QColor("#18181b"))
        widget = QtWidgets.QSplashScreen(pixmap)
        widget.setParent(parent)
        widget.setWindowFlags(_native_widget_flag())
        widget.setPixmap(pixmap)
        widget.setFixedSize(pixmap.size())
        alignment = getattr(QtCore.Qt, "AlignCenter", None)
        if alignment is None:
            alignment = QtCore.Qt.AlignmentFlag.AlignCenter
        widget.showMessage(
            "shadcn-qt\nLoading native components…",
            alignment,
            QtGui.QColor("#fafafa"),
        )
    else:
        raise KeyError(name)
    return widget


def _set_embedded_dialog(widget: Any) -> Any:
    widget.setWindowFlags(_native_widget_flag())
    set_modal = getattr(widget, "setModal", None)
    if callable(set_modal):
        set_modal(False)
    widget.setMinimumWidth(560)
    widget.setMinimumHeight(300)
    return widget


def _native_dialog_specimen(name: str, parent: Any) -> Any:
    if name == "QMessageBox":
        widget = QtWidgets.QMessageBox(parent)
        widget.setWindowTitle("Confirm workspace")
        widget.setText("Create the new workspace?")
        widget.setInformativeText("Existing files will remain unchanged.")
        widget.setStandardButtons(_native_message_buttons("Cancel", "Ok"))
    elif name == "QFileDialog":
        widget = QtWidgets.QFileDialog(parent, "Choose a project folder")
        widget.setOption(
            _native_enum(QtWidgets.QFileDialog, "DontUseNativeDialog", "Option"),
            True,
        )
    elif name == "QColorDialog":
        widget = QtWidgets.QColorDialog(QtGui.QColor("#18181b"), parent)
        widget.setOption(
            _native_enum(
                QtWidgets.QColorDialog,
                "DontUseNativeDialog",
                "ColorDialogOption",
            ),
            True,
        )
    elif name == "QFontDialog":
        widget = QtWidgets.QFontDialog(parent)
        widget.setOption(
            _native_enum(
                QtWidgets.QFontDialog,
                "DontUseNativeDialog",
                "FontDialogOption",
            ),
            True,
        )
    elif name == "QInputDialog":
        widget = QtWidgets.QInputDialog(parent)
        widget.setWindowTitle("Workspace name")
        widget.setLabelText("Name")
        widget.setTextValue("shadcn-qt")
    elif name == "QProgressDialog":
        widget = QtWidgets.QProgressDialog(
            "Indexing components…", "Cancel", 0, 100, parent
        )
        widget.setAutoClose(False)
        widget.setMinimumDuration(100000)
        widget.setValue(64)
    elif name == "QErrorMessage":
        widget = QtWidgets.QErrorMessage(parent)
        message = widget.findChild(QtWidgets.QLabel)
        if message is not None:
            message.setText("The selected theme file could not be loaded.")
    else:
        raise KeyError(name)
    return _set_embedded_dialog(widget)


def _native_individual_specimen(name: str, parent: Any) -> Any:
    if name in NATIVE_FORM_NAMES:
        return _native_form_specimen(name, parent)
    if name in NATIVE_DATA_VIEW_NAMES:
        return _native_data_specimen(name, parent)
    if name in NATIVE_CONTAINER_NAMES:
        return _native_container_specimen(name, parent)
    if name in NATIVE_WINDOW_NAMES:
        return _native_window_specimen(name, parent)
    if name in NATIVE_DIALOG_NAMES:
        return _native_dialog_specimen(name, parent)
    raise KeyError(name)


def build_native_preview(name: str, parent: Any = None) -> Any:
    """Build a preview composed exclusively from stock QtWidgets classes."""

    if name not in native_preview_names():
        raise KeyError(f"Unknown native gallery preview: {name}")
    host, layout = _preview_host(parent)

    if name in native_individual_preview_names():
        specimen_group, specimen_layout = _native_group(name, host)
        specimen_layout.addWidget(
            QtWidgets.QLabel(
                f"Stock {name} · automatically adopted by shadcn-qt", specimen_group
            )
        )
        specimen = _native_individual_specimen(name, specimen_group)
        expected_type = getattr(QtWidgets, name)
        target = getattr(specimen, "_native_gallery_target", None)
        if not isinstance(target, expected_type):
            target = (
                specimen
                if isinstance(specimen, expected_type)
                else specimen.findChild(expected_type)
            )
        if target is None:
            raise RuntimeError(f"Native preview {name} did not create a {name}")
        target.setObjectName(f"nativeGallery{name}")
        specimen_layout.addWidget(specimen)
        layout.addWidget(specimen_group)

    elif name == "Native Forms":
        editors, editors_layout = _native_group("Editors and selectors", host)
        line_edit = QtWidgets.QLineEdit(editors)
        line_edit.setPlaceholderText("name@example.com")
        invalid = QtWidgets.QLineEdit("Invalid value", editors)
        invalid.setProperty("invalid", True)
        combo = QtWidgets.QComboBox(editors)
        combo.addItems(["PySide6", "PyQt6", "PySide2", "PyQt5"])
        editable_combo = QtWidgets.QComboBox(editors)
        editable_combo.setEditable(True)
        editable_combo.addItems(["New York", "Shanghai", "London"])
        font_combo = QtWidgets.QFontComboBox(editors)
        spin = QtWidgets.QSpinBox(editors)
        spin.setRange(0, 100)
        spin.setValue(24)
        double_spin = QtWidgets.QDoubleSpinBox(editors)
        double_spin.setValue(12.5)
        date = QtWidgets.QDateEdit(QtCore.QDate(2026, 8, 14), editors)
        date.setCalendarPopup(True)
        time = QtWidgets.QTimeEdit(QtCore.QTime(9, 30), editors)
        date_time = QtWidgets.QDateTimeEdit(
            QtCore.QDateTime(QtCore.QDate(2026, 8, 14), QtCore.QTime(9, 30)),
            editors,
        )
        date_time.setCalendarPopup(True)
        shortcut = QtWidgets.QKeySequenceEdit(editors)
        shortcut.setKeySequence(QtGui.QKeySequence("Ctrl+K"))
        for label, widget in (
            ("QLineEdit", line_edit),
            ("Invalid QLineEdit", invalid),
            ("QComboBox", combo),
            ("Editable QComboBox", editable_combo),
            ("QFontComboBox", font_combo),
            ("QSpinBox", spin),
            ("QDoubleSpinBox", double_spin),
            ("QDateEdit", date),
            ("QTimeEdit", time),
            ("QDateTimeEdit", date_time),
            ("QKeySequenceEdit", shortcut),
        ):
            _add_native_form_control(editors_layout, label, widget, editors)
        layout.addWidget(editors)

        actions, actions_layout = _native_group("Actions and choices", host)
        for text, variant in (
            ("Primary", "default"),
            ("Secondary", "secondary"),
            ("Outline", "outline"),
        ):
            button = QtWidgets.QPushButton(text, actions)
            button.setProperty("variant", variant)
            _add_native_form_control(
                actions_layout, f"QPushButton · {text}", button, actions
            )
        command = QtWidgets.QCommandLinkButton(
            "Open workspace", "Continue with an existing project", actions
        )
        tool = QtWidgets.QToolButton(actions)
        tool.setText("Tool action")
        check = QtWidgets.QCheckBox("Notifications", actions)
        check.setChecked(True)
        partial = QtWidgets.QCheckBox("Inherited", actions)
        partial.setTristate(True)
        partial_state = getattr(QtCore.Qt, "PartiallyChecked", None)
        if partial_state is None:
            partial_state = QtCore.Qt.CheckState.PartiallyChecked
        partial.setCheckState(partial_state)
        radio = QtWidgets.QRadioButton("Team plan", actions)
        radio.setChecked(True)
        slider = QtWidgets.QSlider(_native_horizontal(), actions)
        slider.setValue(64)
        dial = QtWidgets.QDial(actions)
        dial.setValue(64)
        dial.setNotchesVisible(True)
        dial.setFixedSize(120, 120)
        scrollbar = QtWidgets.QScrollBar(_native_horizontal(), actions)
        scrollbar.setValue(40)
        progress = QtWidgets.QProgressBar(actions)
        progress.setValue(64)
        dialog_buttons = QtWidgets.QDialogButtonBox(
            _native_standard_buttons("Cancel", "Save"), actions
        )
        lcd = QtWidgets.QLCDNumber(actions)
        lcd.display(2026)
        lcd.setFixedHeight(80)
        for label, widget in (
            ("QCommandLinkButton", command),
            ("QToolButton", tool),
            ("QCheckBox · checked", check),
            ("QCheckBox · partially checked", partial),
            ("QRadioButton", radio),
            ("QSlider", slider),
            ("QDial", dial),
            ("QScrollBar", scrollbar),
            ("QProgressBar", progress),
            ("QDialogButtonBox", dialog_buttons),
            ("QLCDNumber", lcd),
        ):
            _add_native_form_control(actions_layout, label, widget, actions)
        layout.addWidget(actions)

        text_group, text_layout = _native_group("Text editors", host)
        plain = QtWidgets.QPlainTextEdit(text_group)
        plain.setPlainText("QPlainTextEdit keeps its native document API.")
        rich = QtWidgets.QTextEdit(text_group)
        rich.setHtml("<b>QTextEdit</b><br>Rich text remains available.")
        browser = QtWidgets.QTextBrowser(text_group)
        browser.setHtml("<b>QTextBrowser</b><br>Read-only document navigation.")
        for label, editor in (
            ("QPlainTextEdit", plain),
            ("QTextEdit", rich),
            ("QTextBrowser", browser),
        ):
            editor.setFixedHeight(110)
            _add_native_form_control(text_layout, label, editor, text_group)
        layout.addWidget(text_group)

    elif name == "Native Data Views":
        top = QtWidgets.QWidget(host)
        top_layout = QtWidgets.QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(14)

        list_group, list_layout = _native_group("Lists and trees", top)
        list_widget = QtWidgets.QListWidget(list_group)
        list_widget.addItems(["Overview", "Activity", "Settings", "Billing"])
        list_widget.setCurrentRow(1)
        tree = QtWidgets.QTreeWidget(list_group)
        tree.setHeaderLabels(["Workspace", "Status"])
        project = QtWidgets.QTreeWidgetItem(["shadcn-qt", "Active"])
        project.addChild(QtWidgets.QTreeWidgetItem(["Python", "Ready"]))
        project.addChild(QtWidgets.QTreeWidgetItem(["C++", "Planned"]))
        tree.addTopLevelItem(project)
        project.setExpanded(True)
        list_layout.addWidget(list_widget)
        list_layout.addWidget(tree)
        top_layout.addWidget(list_group, 1)

        table_group, table_layout = _native_group("Tables and columns", top)
        table = QtWidgets.QTableWidget(3, 3, table_group)
        table.setHorizontalHeaderLabels(["Component", "Binding", "State"])
        for row, values in enumerate(
            (
                ("Button", "PySide6", "Ready"),
                ("Calendar", "PyQt6", "Ready"),
                ("Dialog", "Qt 5/6", "Ready"),
            )
        ):
            for column, value in enumerate(values):
                table.setItem(row, column, QtWidgets.QTableWidgetItem(value))
        table.horizontalHeader().setStretchLastSection(True)
        model = QtGui.QStandardItemModel(table_group)
        root = QtGui.QStandardItem("Workspace")
        source = QtGui.QStandardItem("packages")
        source.appendRow(QtGui.QStandardItem("python"))
        source.appendRow(QtGui.QStandardItem("cpp"))
        root.appendRow(source)
        model.appendRow(root)
        columns = QtWidgets.QColumnView(table_group)
        columns.setModel(model)
        columns.setCurrentIndex(root.index())
        columns.setMaximumHeight(120)
        table_layout.addWidget(table)
        table_layout.addWidget(columns)
        top_layout.addWidget(table_group, 1)
        layout.addWidget(top)

        bottom = QtWidgets.QWidget(host)
        bottom_layout = QtWidgets.QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(14)
        calendar_group, calendar_layout = _native_group("Calendar", bottom)
        calendar = QtWidgets.QCalendarWidget(calendar_group)
        calendar.setSelectedDate(QtCore.QDate(2026, 8, 14))
        calendar.setMaximumHeight(260)
        calendar_layout.addWidget(calendar)
        bottom_layout.addWidget(calendar_group, 1)
        browser_group, browser_layout = _native_group("Document and scrolling", bottom)
        browser = QtWidgets.QTextBrowser(browser_group)
        browser.setHtml(
            "<h3>Native document</h3><p>Links, selection, scrolling, and the "
            "QTextDocument model remain unchanged.</p><ul><li>new-york geometry</li>"
            "<li>Zinc semantic colors</li><li>reversible adoption</li></ul>"
        )
        browser_layout.addWidget(browser)
        bottom_layout.addWidget(browser_group, 1)
        layout.addWidget(bottom)

    elif name == "Native Containers":
        top = QtWidgets.QWidget(host)
        top_layout = QtWidgets.QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(14)
        tabs = QtWidgets.QTabWidget(top)
        tabs.setDocumentMode(True)
        tabs.setMovable(True)
        tabs.setTabsClosable(True)
        for title in ("Account", "Security", "Billing", "Activity"):
            page = QtWidgets.QWidget(tabs)
            page_layout = QtWidgets.QVBoxLayout(page)
            page_layout.addWidget(QtWidgets.QLabel(f"{title} settings", page))
            page_layout.addWidget(QtWidgets.QLineEdit(page))
            page_layout.addStretch(1)
            tabs.addTab(page, title)
        tabs.tabCloseRequested.connect(tabs.removeTab)
        top_layout.addWidget(tabs, 1)
        toolbox = QtWidgets.QToolBox(top)
        for title, body in (
            ("Profile", "Public account details"),
            ("Notifications", "Email and push settings"),
            ("Advanced", "Developer options"),
        ):
            page = QtWidgets.QWidget(toolbox)
            page_layout = QtWidgets.QVBoxLayout(page)
            page_layout.addWidget(QtWidgets.QLabel(body, page))
            page_layout.addStretch(1)
            toolbox.addItem(page, title)
        top_layout.addWidget(toolbox, 1)
        layout.addWidget(top)

        splitter = QtWidgets.QSplitter(_native_horizontal(), host)
        group = QtWidgets.QGroupBox("Native group box", splitter)
        group_layout = QtWidgets.QVBoxLayout(group)
        group_layout.addWidget(QtWidgets.QCheckBox("Preserve signals", group))
        group_layout.addWidget(QtWidgets.QRadioButton("Use Qt models", group))
        scroll = QtWidgets.QScrollArea(splitter)
        scroll.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget(scroll)
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        for index in range(1, 8):
            scroll_layout.addWidget(
                QtWidgets.QLabel(f"Scrollable native row {index}", scroll_content)
            )
        scroll_layout.addStretch(1)
        scroll.setWidget(scroll_content)
        splitter.addWidget(group)
        splitter.addWidget(scroll)
        splitter.setSizes([300, 420])
        splitter.setMinimumHeight(190)
        layout.addWidget(splitter)

        advanced = QtWidgets.QWidget(host)
        advanced_layout = QtWidgets.QHBoxLayout(advanced)
        advanced_layout.setContentsMargins(0, 0, 0, 0)
        advanced_layout.setSpacing(14)
        mdi = QtWidgets.QMdiArea(advanced)
        mdi.setMinimumHeight(150)
        first = QtWidgets.QMdiSubWindow(mdi)
        first.setWindowTitle("Native MDI")
        first.setWidget(QtWidgets.QLabel("Subwindow content", first))
        mdi.addSubWindow(first)
        first.show()
        graphics = QtWidgets.QGraphicsView(advanced)
        scene = QtWidgets.QGraphicsScene(graphics)
        path = QtGui.QPainterPath()
        path.addRoundedRect(20, 20, 160, 72, 6, 6)
        scene.addPath(path)
        scene.addText("QGraphicsView")
        graphics.setScene(scene)
        advanced_layout.addWidget(mdi, 1)
        advanced_layout.addWidget(graphics, 1)
        layout.addWidget(advanced)

    elif name == "Native Window Chrome":
        shell = QtWidgets.QMainWindow(host)
        shell.setWindowFlags(_native_widget_flag())
        shell.setMinimumHeight(290)
        shell.menuBar().addMenu("File").addAction("New project")
        shell.menuBar().addMenu("Edit").addAction("Preferences")
        toolbar = QtWidgets.QToolBar("Workspace", shell)
        toolbar.addAction("New")
        toolbar.addAction("Open")
        toolbar.addSeparator()
        toolbar.addAction("Save")
        shell.addToolBar(toolbar)
        center = QtWidgets.QWidget(shell)
        center_layout = QtWidgets.QVBoxLayout(center)
        center_layout.addWidget(QtWidgets.QLabel("QMainWindow central content", center))
        center_layout.addWidget(QtWidgets.QLineEdit("Native window surface", center))
        center_layout.addStretch(1)
        shell.setCentralWidget(center)
        dock = QtWidgets.QDockWidget("Inspector", shell)
        dock.setWidget(QtWidgets.QListWidget(dock))
        dock.widget().addItems(["Geometry", "Appearance", "Accessibility"])
        right_area = getattr(QtCore.Qt, "RightDockWidgetArea", None)
        if right_area is None:
            right_area = QtCore.Qt.DockWidgetArea.RightDockWidgetArea
        shell.addDockWidget(right_area, dock)
        shell.statusBar().showMessage("Ready · native signals and window chrome")
        layout.addWidget(shell)

        specimens = QtWidgets.QWidget(host)
        specimens_layout = QtWidgets.QHBoxLayout(specimens)
        specimens_layout.setContentsMargins(0, 0, 0, 0)
        specimens_layout.setSpacing(14)
        dialog = QtWidgets.QDialog(specimens)
        dialog.setWindowFlags(_native_widget_flag())
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
        dialog_layout.addWidget(_native_heading("Embedded QDialog", dialog))
        dialog_layout.addWidget(
            QtWidgets.QLabel("The same adapter styles real top-level dialogs.", dialog)
        )
        dialog_layout.addStretch(1)
        dialog_layout.addWidget(
            QtWidgets.QDialogButtonBox(
                _native_standard_buttons("Cancel", "Ok"), dialog
            )
        )
        specimens_layout.addWidget(dialog, 1)
        wizard = QtWidgets.QWizard(specimens)
        wizard.setWindowFlags(_native_widget_flag())
        wizard.setWindowTitle("QWizard")
        page = QtWidgets.QWizardPage(wizard)
        page.setTitle("Create a workspace")
        page.setSubTitle("Wizard pages retain their standard navigation API.")
        page_layout = QtWidgets.QVBoxLayout(page)
        page_layout.addWidget(QtWidgets.QLineEdit(page))
        wizard.addPage(page)
        specimens_layout.addWidget(wizard, 1)
        layout.addWidget(specimens)

    layout.addStretch(1)
    host.setProperty("gallery_component", name)
    host.setProperty("gallery_native_preview", True)
    return host


class GalleryWindow(QtWidgets.QMainWindow):
    """Searchable interactive window for the complete public component catalog."""

    def __init__(
        self,
        *,
        theme: str = "light",
        component: str = "Button",
        group_expansion_mode: str = "single-click",
    ) -> None:
        super().__init__()
        app = QtWidgets.QApplication.instance()
        if app is None:
            raise RuntimeError("Create QApplication before GalleryWindow")
        enable_native_widget_styling(app)
        self._role = _user_role()
        self._current_component = ""
        self._navigation_items: Dict[str, Any] = {}
        self.setWindowTitle(
            f"shadcn-qt {__version__} · {STYLE_PROFILE} + {BASE_COLOR.title()}"
        )
        self.resize(1220, 820)
        self.setMinimumSize(940, 640)

        central = QtWidgets.QWidget(self)
        central.setObjectName("galleryRoot")
        self.setCentralWidget(central)
        root = QtWidgets.QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = QtWidgets.QWidget(central)
        self.sidebar.setObjectName("gallerySidebar")
        self.sidebar.setMinimumWidth(270)
        self.sidebar.setMaximumWidth(320)
        sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(18, 20, 18, 18)
        sidebar_layout.setSpacing(12)
        sidebar_layout.addWidget(
            ui.Typography("shadcn-qt", self.sidebar, level="h3")
        )
        sidebar_layout.addWidget(
            ui.Label("Component Gallery", self.sidebar, variant="muted")
        )
        self.search = ui.Input(self.sidebar)
        self.search.setPlaceholderText(f"Search {len(gallery_names())} components…")
        sidebar_layout.addWidget(self.search)
        self.navigation = _GalleryNavigationTree(self.sidebar)
        self.navigation.setObjectName("galleryNavigation")
        self.navigation.setHeaderHidden(True)
        self.navigation.setIndentation(14)
        self.navigation.set_expansion_mode(group_expansion_mode)
        sidebar_layout.addWidget(self.navigation, 1)
        expansion_settings = QtWidgets.QWidget(self.sidebar)
        expansion_settings_layout = QtWidgets.QHBoxLayout(expansion_settings)
        expansion_settings_layout.setContentsMargins(0, 0, 0, 0)
        expansion_settings_layout.setSpacing(8)
        expansion_settings_layout.addWidget(
            ui.Label("Group mode", expansion_settings, variant="muted"),
            1,
        )
        self.expansion_mode_select = ui.Select(expansion_settings)
        self.expansion_mode_select.setAccessibleName("Group expansion mode")
        self.expansion_mode_select.addItems(["Single click", "Double click"])
        self.expansion_mode_select.setFixedWidth(160)
        self.expansion_mode_select.setCurrentText(
            "Double click" if group_expansion_mode == "double-click" else "Single click"
        )
        expansion_settings_layout.addWidget(self.expansion_mode_select)
        sidebar_layout.addWidget(expansion_settings)
        sidebar_layout.addWidget(
            ui.Label(
                f"Core {__version__} · {STYLE_PROFILE} + {BASE_COLOR.title()}",
                self.sidebar,
                variant="muted",
            )
        )
        root.addWidget(self.sidebar)
        self.sidebar_separator = ui.Separator(central, orientation="vertical")
        self.sidebar_separator.setObjectName("gallerySidebarSeparator")
        root.addWidget(self.sidebar_separator)

        content = QtWidgets.QWidget(central)
        content_layout = QtWidgets.QVBoxLayout(content)
        content_layout.setContentsMargins(30, 24, 30, 20)
        content_layout.setSpacing(12)

        header = QtWidgets.QWidget(content)
        header_layout = QtWidgets.QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        titles = QtWidgets.QWidget(header)
        title_layout = QtWidgets.QVBoxLayout(titles)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(3)
        self.component_title = ui.Typography(component, titles, level="h2")
        self.component_summary = ui.Label("", titles, variant="muted")
        self.component_summary.setWordWrap(True)
        title_layout.addWidget(self.component_title)
        title_layout.addWidget(self.component_summary)
        header_layout.addWidget(titles, 1)
        self.category_badge = ui.Badge("", header, variant="secondary")
        header_layout.addWidget(self.category_badge)
        self.theme_select = ui.Select(header)
        self.theme_select.addItems(["Light", "Dark"])
        header_layout.addWidget(self.theme_select)
        content_layout.addWidget(header)
        content_layout.addWidget(ui.Separator(content))

        self.preview_scroll = ui.ScrollArea(content)
        self.preview_canvas = QtWidgets.QWidget(self.preview_scroll)
        self.preview_layout = QtWidgets.QVBoxLayout(self.preview_canvas)
        self.preview_layout.setContentsMargins(0, 8, 12, 8)
        self.preview_layout.setSpacing(0)
        self.preview_scroll.setWidget(self.preview_canvas)
        content_layout.addWidget(self.preview_scroll, 1)
        self.status = ui.Label("", content, variant="muted")
        content_layout.addWidget(self.status)
        root.addWidget(content, 1)

        self._populate_navigation()
        self.search.textChanged.connect(self.filter_components)
        self.navigation.currentItemChanged.connect(self._navigation_changed)
        self.expansion_mode_select.currentTextChanged.connect(
            lambda label: self.set_group_expansion_mode(
                label.casefold().replace(" ", "-")
            )
        )
        self.theme_select.currentTextChanged.connect(
            lambda selected: self.set_theme(selected.lower())
        )
        self.set_theme(theme)
        self.select_component(component if component in gallery_names() else "Button")

    @property
    def current_component(self) -> str:
        return self._current_component

    def group_expansion_mode(self) -> str:
        return self.navigation.get_expansion_mode()

    def set_group_expansion_mode(self, mode: str) -> None:
        self.navigation.set_expansion_mode(mode)
        label = "Double click" if mode == "double-click" else "Single click"
        if self.expansion_mode_select.currentText() != label:
            self.expansion_mode_select.setCurrentText(label)

    def _populate_navigation(self) -> None:
        for category, components in COMPONENT_CATEGORIES + NATIVE_WIDGET_CATEGORIES:
            category_item = QtWidgets.QTreeWidgetItem([category])
            self.navigation.addTopLevelItem(category_item)
            for name in components:
                item = QtWidgets.QTreeWidgetItem([name])
                item.setData(0, self._role, name)
                category_item.addChild(item)
                self._navigation_items[name] = item
            category_item.setExpanded(True)

    def _navigation_changed(self, current: Any, _previous: Any) -> None:
        if current is None:
            return
        name = current.data(0, self._role)
        if name:
            self.show_component(str(name))

    def select_component(self, name: str) -> None:
        if name not in self._navigation_items:
            raise KeyError(name)
        item = self._navigation_items[name]
        self.navigation.setCurrentItem(item)
        if self._current_component != name:
            self.show_component(name)

    def show_component(self, name: str) -> Any:
        category = gallery_category(name)
        _clear_layout(self.preview_layout)
        card = ui.Card(self.preview_canvas)
        card.setObjectName("galleryPreviewCard")
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(12)
        preview = (
            build_native_preview(name, card)
            if name in native_preview_names()
            else build_component_preview(name, card)
        )
        card_layout.addWidget(preview)
        self.preview_layout.addWidget(card)
        self.preview_layout.addStretch(1)
        self.component_title.setText(name)
        self.component_summary.setText(CATEGORY_DESCRIPTIONS[category])
        self.category_badge.setText(category)
        suffix = (
            "stock QtWidgets · automatic reversible styling"
            if name in native_preview_names()
            else "interactive Qt-native preview"
        )
        self.status.setText(f"Showing {name} · {suffix}")
        self._current_component = name
        return preview

    def filter_components(self, text: str) -> None:
        query = text.strip().casefold()
        first_visible = None
        for top_index in range(self.navigation.topLevelItemCount()):
            category_item = self.navigation.topLevelItem(top_index)
            category_match = query in category_item.text(0).casefold()
            visible_children = 0
            for child_index in range(category_item.childCount()):
                child = category_item.child(child_index)
                visible = (
                    not query or category_match or query in child.text(0).casefold()
                )
                child.setHidden(not visible)
                if visible:
                    visible_children += 1
                    if first_visible is None:
                        first_visible = child
            category_item.setHidden(visible_children == 0)
            if visible_children:
                category_item.setExpanded(True)
        current = self.navigation.currentItem()
        if first_visible is not None and (current is None or current.isHidden()):
            self.navigation.setCurrentItem(first_visible)

    def visible_component_names(self) -> List[str]:
        return [
            name
            for name, item in self._navigation_items.items()
            if not item.isHidden() and not item.parent().isHidden()
        ]

    def set_theme(self, theme: str) -> None:
        if theme not in {"light", "dark"}:
            raise ValueError("theme must be 'light' or 'dark'")
        app = QtWidgets.QApplication.instance()
        if app is None:
            raise RuntimeError("Create QApplication before GalleryWindow")
        apply_theme(app, theme, extra_qss=GALLERY_QSS)
        label = theme.title()
        if self.theme_select.currentText() != label:
            previous = self.theme_select.blockSignals(True)
            self.theme_select.setCurrentText(label)
            self.theme_select.blockSignals(previous)
        app.setProperty("shadcn_qt_gallery_theme", theme)

    def save_screenshot(self, path: Path) -> bool:
        path.parent.mkdir(parents=True, exist_ok=True)
        return self.grab().save(str(path))


def _parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", choices=("light", "dark"), default="light")
    parser.add_argument("--component", choices=gallery_names(), default="Button")
    parser.add_argument(
        "--screenshot", type=Path, help="Save the shown gallery window and exit"
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parse_args(argv)
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = GalleryWindow(theme=args.theme, component=args.component)
    window.show()
    if args.screenshot is not None:

        def capture() -> None:
            if not window.save_screenshot(args.screenshot):
                raise RuntimeError(f"Could not save screenshot to {args.screenshot}")
            app.quit()

        QtCore.QTimer.singleShot(350, capture)
    return int(app_exec(app))


if __name__ == "__main__":
    raise SystemExit(main())
