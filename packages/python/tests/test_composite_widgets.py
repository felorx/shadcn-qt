import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="module")
def runtime():
    try:
        from qtshadcn._qt import QtWidgets
    except ImportError as exc:
        pytest.skip(str(exc))
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app, QtWidgets


def test_full_catalog_constructs(runtime):
    from qtshadcn import widgets

    instances = [getattr(widgets, name)() for name in widgets.__all__]
    assert len(instances) >= 65
    assert all(widget.property("qtshadcn_component") for widget in instances)


def test_special_catalog_mappings(runtime):
    from qtshadcn.widgets import Chart, Direction, Typography

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
    _, QtWidgets = runtime
    from qtshadcn import Accordion, Carousel, Pagination

    accordion = Accordion()
    first = accordion.addItem(QtWidgets.QLabel("One"), "First")
    second = accordion.addItem(QtWidgets.QLabel("Two"), "Second")
    second.setExpanded(True)
    assert second.expanded is True
    assert first.expanded is False
    assert accordion.currentIndex() == 1

    carousel = Carousel()
    carousel.addWidget(QtWidgets.QLabel("One"))
    carousel.addWidget(QtWidgets.QLabel("Two"))
    carousel.next()
    assert carousel.currentIndex() == 1
    carousel.next()
    assert carousel.currentIndex() == 0

    pagination = Pagination(page_count=4)
    pagination.setPage(3)
    pagination.next()
    assert pagination.currentPage == 4
    assert not pagination.nextButton.isEnabled()


def test_form_compositions(runtime):
    from qtshadcn import Field, Input, InputOTP, RadioGroup, ToggleGroup

    otp = InputOTP(length=4)
    otp.setText("1234")
    assert otp.value == "1234"
    otp.codeLength = 6
    assert otp.codeLength == 6

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
    from qtshadcn import Command, DataTable, Message, MessageScroller

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
    from qtshadcn import AlertDialog, Sheet, Sonner, apply_theme

    dialog = AlertDialog()
    assert dialog.title == "Are you sure?"
    sheet = Sheet(side="left")
    assert sheet.side == "left"
    sonner = Sonner()
    toast = sonner.toast("Saved", "Changes persisted", duration=0)
    assert toast.isVisible() or not sonner.isVisible()

    apply_theme(app, "dark")
    stylesheet = app.styleSheet()
    assert 'qtshadcn_component="dialog"' in stylesheet
    assert 'qtshadcn_component="skeleton"' in stylesheet
    assert 'qtshadcn_component="data-table"' in stylesheet
