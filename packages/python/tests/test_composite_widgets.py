import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="module")
def runtime():
    try:
        from shadcn_qt._qt import QtWidgets
    except ImportError as exc:
        pytest.skip(str(exc))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app, QtWidgets


def test_full_catalog_constructs(runtime):
    from shadcn_qt import widgets

    instances = [getattr(widgets, name)() for name in widgets.__all__]
    assert len(instances) >= 65
    assert all(widget.property("shadcn_qt_component") for widget in instances)


def test_special_catalog_mappings(runtime):
    from shadcn_qt.widgets import Chart, Direction, Typography

    chart = Chart(chart_type="bar", values="1, 3, 2")
    assert chart.valuesList() == [1.0, 3.0, 2.0]
    chart.resize(240, 140)
    chart.show()
    runtime[0].processEvents()
    assert not chart.grab().isNull()
    chart.chartType = "line"
    assert chart.chartType == "line"

    direction = Direction(direction="rtl")
    assert direction.direction == "rtl"

    heading = Typography("Title", level="h1")
    assert heading.level == "h1"


def test_accordion_carousel_and_pagination(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import Accordion, Carousel, Pagination
    from shadcn_qt._qt import QtCore

    accordion = Accordion()
    first = accordion.addItem(QtWidgets.QLabel("One"), "First")
    second = accordion.addItem(QtWidgets.QLabel("Two"), "Second")
    second.setExpanded(True)
    assert second.expanded is True
    assert first.expanded is False
    assert accordion.currentIndex() == 1
    accordion.resize(420, accordion.sizeHint().height())
    accordion.show()
    app.processEvents()
    assert first.trigger.text() == "First"
    assert first.trigger._icon_name == "chevron-down"
    first_icon_bounds = first.trigger._icon_path().boundingRect()
    assert (first_icon_bounds.width(), first_icon_bounds.height()) == (8.0, 4.0)
    assert first_icon_bounds.center() == first.trigger._icon_rect().center()

    carousel = Carousel()
    carousel.addWidget(QtWidgets.QLabel("One"))
    carousel.addWidget(QtWidgets.QLabel("Two"))
    carousel.next()
    assert carousel.currentIndex() == 1
    carousel.next()
    assert carousel.currentIndex() == 0
    carousel.resize(420, 180)
    carousel.show()
    app.processEvents()
    for button, accessible_name in (
        (carousel.previousButton, "Previous slide"),
        (carousel.nextButton, "Next slide"),
    ):
        assert button.text() == ""
        assert button.accessibleName() == accessible_name
        icon_bounds = button._icon_path().boundingRect()
        assert (icon_bounds.width(), icon_bounds.height()) == (4.0, 8.0)
        assert icon_bounds.center() == QtCore.QRectF(button.rect()).center()

    pagination = Pagination(page_count=4)
    pagination.setPage(3)
    pagination.next()
    assert pagination.currentPage == 4
    assert not pagination.nextButton.isEnabled()


def test_component_sources_do_not_use_font_icon_glyphs():
    widget_root = Path(__file__).parents[1] / "shadcn_qt" / "widgets"
    banned = set("▴▾‹›×✕✖✓✔▲▼◀▶⌃⌄")
    offenders = []
    for source_path in widget_root.glob("*.py"):
        text = source_path.read_text(encoding="utf-8")
        used = sorted(banned.intersection(text))
        if used:
            offenders.append(f"{source_path.name}: {''.join(used)}")
    assert not offenders, "font-backed UI icons found: " + ", ".join(offenders)


def test_form_compositions(runtime):
    app, QtWidgets = runtime
    from shadcn_qt import (
        Field,
        Input,
        InputGroup,
        InputOTP,
        RadioGroup,
        ToggleGroup,
        apply_theme,
    )

    apply_theme(app, "light")
    otp = InputOTP(length=4)
    otp.setText("1234")
    assert otp.value == "1234"
    otp.codeLength = 6
    assert otp.codeLength == 6
    otp.resize(600, 36)
    otp.show()
    app.processEvents()
    assert otp.sizeHint().height() == 36
    assert otp.height() == 36
    assert all(
        edit.minimumHeight() == 36
        and edit.maximumHeight() == 36
        and edit.height() == 36
        for edit in otp._edits
    )
    assert [edit.x() for edit in otp._edits] == [0, 36, 72, 108, 144, 180]
    assert otp._edits[0].property("otpPosition") == "first"
    assert otp._edits[-1].property("otpPosition") == "last"
    assert all(
        right.x() == left.x() + left.width()
        for left, right in zip(otp._edits, otp._edits[1:])
    )
    otp_image = otp.grab().toImage()
    center_y = otp._edits[0].height() // 2
    assert otp_image.pixelColor(0, center_y) != otp_image.pixelColor(3, center_y)
    selected_slot = otp._edits[2]
    selected_slot.setFocus()
    selected_slot.selectAll()
    app.processEvents()
    option = QtWidgets.QStyleOptionFrame()
    selected_slot.initStyleOption(option)
    line_edit_contents = getattr(QtWidgets.QStyle, "SE_LineEditContents", None)
    if line_edit_contents is None:
        line_edit_contents = QtWidgets.QStyle.SubElement.SE_LineEditContents
    content_rect = selected_slot.style().subElementRect(
        line_edit_contents, option, selected_slot
    )
    assert content_rect.width() >= 28
    assert content_rect.width() >= selected_slot.fontMetrics().horizontalAdvance("8") * 3

    input_group = InputGroup()
    input_group.prefix = "@"
    input_group.suffix = ".com"
    input_group.resize(360, 36)
    input_group.show()
    input_group.input.setFocus()
    app.processEvents()
    assert input_group.property("focused")
    group_image = input_group.grab().toImage()
    pixel_ratio = group_image.devicePixelRatio()
    input_left = int(input_group.input.x() * pixel_ratio)
    group_center_y = group_image.height() // 2
    assert group_image.pixelColor(input_left, group_center_y) == group_image.pixelColor(
        input_left + max(6, int(6 * pixel_ratio)), group_center_y
    )

    field = Field(label="Email", description="Work address")
    field.setControl(Input())
    field.required = True
    field.error = "Invalid address"
    assert field.required
    assert field.property("invalid")

    radios = RadioGroup()
    radios.addOption("one", "One")
    radios.addOption("two", "Two")
    radios.setValue("two")
    assert radios.selectedValue == "two"

    toggles = ToggleGroup()
    toggles.addItem("bold", "B")
    toggles.addItem("italic", "I")
    toggles.setValue("bold")
    assert toggles.value() == "bold"


def test_data_command_and_conversation(runtime):
    from shadcn_qt import Attachment, Command, DataTable, Message, MessageScroller
    from shadcn_qt._qt import QtCore

    attachment = Attachment(name="report.pdf")
    attachment.resize(360, attachment.sizeHint().height())
    attachment.show()
    runtime[0].processEvents()
    assert attachment.removeButton.text() == ""
    assert attachment.removeButton.accessibleName() == "Remove attachment"
    remove_icon_bounds = attachment.removeButton._icon_path().boundingRect()
    assert (remove_icon_bounds.width(), remove_icon_bounds.height()) == (7.0, 7.0)
    assert remove_icon_bounds.center() == QtCore.QRectF(
        attachment.removeButton.rect()
    ).center()

    table = DataTable()
    table.setRows(["Name", "Role"], [["Ada", "Admin"], ["Lin", "User"]])
    assert table.model().rowCount() == 2
    table.setFilterText("Ada")
    assert table.model().rowCount() == 1

    command = Command()
    command.setItems([("Open file", "open"), ("Save file", "save")])
    command.search.setText("save")
    assert command.list.item(0).isHidden()
    assert not command.list.item(1).isHidden()

    scroller = MessageScroller()
    message = Message(author="Ada", content="Hello")
    scroller.addMessage(message)
    assert message.author == "Ada"
    assert message.content == "Hello"


def test_overlay_and_theme_styles(runtime):
    app, _ = runtime
    from shadcn_qt import AlertDialog, Sheet, Sonner, apply_theme
    from shadcn_qt._qt import QtCore

    dialog = AlertDialog()
    assert dialog.title == "Are you sure?"
    sheet = Sheet(side="left")
    assert sheet.side == "left"
    sonner = Sonner()
    toast = sonner.toast("Saved", "Changes persisted", duration=0)
    assert toast.isVisible() or not sonner.isVisible()
    close_center = QtCore.QRectF(toast.closeButton.rect()).center()
    icon_center = toast.closeButton._icon_path().boundingRect().center()
    assert icon_center == close_center
    assert toast.closeButton.accessibleName() == "Close"
    assert not toast.closeButton.grab().isNull()

    apply_theme(app, "dark")
    stylesheet = app.styleSheet()
    assert 'shadcn_qt_component="dialog"' in stylesheet
    assert 'shadcn_qt_component="skeleton"' in stylesheet
    assert 'shadcn_qt_component="data-table"' in stylesheet
