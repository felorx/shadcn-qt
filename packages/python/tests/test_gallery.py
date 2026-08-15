import inspect
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest


@pytest.fixture(scope="module")
def gallery_runtime():
    try:
        from shadcn_qt._qt import QtWidgets
    except ImportError as exc:
        pytest.skip(str(exc))

    from examples.python_gallery import run as gallery

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app, gallery


def test_gallery_covers_public_widget_catalog(gallery_runtime):
    _, gallery = gallery_runtime
    from shadcn_qt import widgets

    assert len(gallery.component_names()) == 66
    assert len(set(gallery.component_names())) == 66
    assert set(gallery.component_names()) == set(widgets.__all__)


def test_gallery_constructs_every_interactive_preview(gallery_runtime):
    app, gallery = gallery_runtime
    window = gallery.GalleryWindow()
    window.show()

    for name in gallery.component_names():
        preview = window.show_component(name)
        app.processEvents()
        assert preview.property("gallery_component") == name
        assert window.current_component == name

    assert not window.grab().isNull()
    window.close()


def test_gallery_search_and_theme_controls(gallery_runtime):
    app, gallery = gallery_runtime
    window = gallery.GalleryWindow(theme="light", component="Chart")
    assert tuple(gallery.COLOR_THEME_PRESETS) == (
        "zinc",
        "blue",
        "violet",
        "emerald",
        "orange",
        "rose",
    )
    surface_tokens = {
        "background",
        "foreground",
        "card",
        "cardForeground",
        "popover",
        "popoverForeground",
        "secondary",
        "secondaryForeground",
        "muted",
        "mutedForeground",
        "border",
        "input",
    }
    for preset_name, preset in gallery.COLOR_THEME_PRESETS.items():
        if preset_name == "zinc":
            continue
        assert surface_tokens <= set(preset["light"])
        assert surface_tokens <= set(preset["dark"])
    assert window.color_theme == "zinc"
    assert window.color_theme_select.currentText() == "Zinc"
    window.filter_components("message")
    assert window.visible_component_names() == [
        "Message",
        "MessageScroller",
        "QMessageBox",
        "QErrorMessage",
    ]

    window.set_color_theme("violet")
    assert window.color_theme == "violet"
    assert window.color_theme_select.currentText() == "Violet"
    assert app.property("shadcn_qt_gallery_color_theme") == "violet"
    assert app.property("shadcn_qt_color_primary") == "#7c3aed"
    assert app.property("shadcn_qt_color_ring") == "#8b5cf6"
    assert app.property("shadcn_qt_color_background") == "#fbfaff"
    assert app.property("shadcn_qt_color_card") == "#fefcff"
    assert app.property("shadcn_qt_color_border") == "#ddd6fe"

    window.set_theme("dark")
    assert app.property("shadcn_qt_gallery_theme") == "dark"
    assert window.theme_select.currentText() == "Dark"
    assert app.property("shadcn_qt_color_primary") == "#8b5cf6"
    assert app.property("shadcn_qt_color_accent") == "#2b1842"
    assert app.property("shadcn_qt_color_background") == "#100d16"
    assert app.property("shadcn_qt_color_card") == "#17121f"
    palette_type = gallery.QtGui.QPalette
    window_role = getattr(palette_type, "Window", None)
    if window_role is None:
        window_role = palette_type.ColorRole.Window
    assert app.palette().color(window_role).name() == "#100d16"

    window.color_theme_select.setCurrentText("Emerald")
    app.processEvents()
    assert window.color_theme == "emerald"
    assert app.property("shadcn_qt_color_primary") == "#10b981"
    assert app.property("shadcn_qt_color_ring") == "#34d399"
    assert app.property("shadcn_qt_color_background") == "#08120f"
    assert app.property("shadcn_qt_color_card") == "#0c1814"
    assert app.property("shadcn_qt_color_input") == "#2b5a48"
    with pytest.raises(ValueError):
        window.set_color_theme("unknown")
    window.close()


def test_gallery_color_theme_cli_option(gallery_runtime):
    _, gallery = gallery_runtime
    args = gallery._parse_args(
        ["--theme", "dark", "--color-theme", "rose", "--component", "Button"]
    )
    assert args.theme == "dark"
    assert args.color_theme == "rose"
    assert args.component == "Button"


def test_gallery_sidebar_uses_a_single_flat_separator(gallery_runtime):
    app, gallery = gallery_runtime
    window = gallery.GalleryWindow()
    window.show()
    app.processEvents()

    assert type(window.sidebar).__name__ == "QWidget"
    assert window.sidebar.property("shadcn_qt_component") != "card"
    assert window.sidebar_separator.get_orientation() == "vertical"
    assert window.sidebar_separator.width() == 1
    assert window.sidebar_separator.height() == window.centralWidget().height()

    window.close()


def test_gallery_navigation_shows_expansion_state(gallery_runtime):
    app, gallery = gallery_runtime
    from shadcn_qt._qt import import_qt_module

    QtCore = gallery.QtCore
    QtTest = import_qt_module("QtTest")
    left_button = getattr(QtCore.Qt, "LeftButton", None)
    if left_button is None:
        left_button = QtCore.Qt.MouseButton.LeftButton
    window = gallery.GalleryWindow()
    window.show()
    app.processEvents()

    category = window.navigation.topLevelItem(0)
    index = window.navigation.indexFromItem(category)
    assert category.isExpanded()
    assert window.navigation.branch_icon_name(index) == "chevron-down"
    assert not window.navigation.expandsOnDoubleClick()
    assert window.group_expansion_mode() == "single-click"
    assert window.expansion_mode_select.currentText() == "Single click"

    category_rect = window.navigation.visualItemRect(category)
    click_position = QtCore.QPoint(
        category_rect.left() + 50,
        category_rect.center().y(),
    )
    QtTest.QTest.mouseClick(
        window.navigation.viewport(),
        left_button,
        pos=click_position,
    )
    app.processEvents()
    assert not category.isExpanded()
    assert window.navigation.branch_icon_name(index) == "chevron-right"

    QtTest.QTest.mouseClick(
        window.navigation.viewport(),
        left_button,
        pos=click_position,
    )
    app.processEvents()
    assert category.isExpanded()
    assert window.navigation.branch_icon_name(index) == "chevron-down"

    window.expansion_mode_select.setCurrentText("Double click")
    app.processEvents()
    assert window.group_expansion_mode() == "double-click"
    QtTest.QTest.mouseClick(
        window.navigation.viewport(),
        left_button,
        pos=click_position,
    )
    app.processEvents()
    assert category.isExpanded()
    QtTest.QTest.mouseDClick(
        window.navigation.viewport(),
        left_button,
        pos=click_position,
    )
    app.processEvents()
    assert not category.isExpanded()
    assert window.navigation.branch_icon_name(index) == "chevron-right"

    window.set_group_expansion_mode("single-click")
    assert window.expansion_mode_select.currentText() == "Single click"
    QtTest.QTest.mouseClick(
        window.navigation.viewport(),
        left_button,
        pos=click_position,
    )
    app.processEvents()
    assert category.isExpanded()
    with pytest.raises(ValueError):
        window.set_group_expansion_mode("hover")
    window.close()


def test_gallery_aspect_ratio_preview_is_visible(gallery_runtime):
    app, gallery = gallery_runtime
    QtWidgets = gallery.QtWidgets
    window = gallery.GalleryWindow(component="AspectRatio")
    window.show()
    app.processEvents()

    preview = window.show_component("AspectRatio")
    app.processEvents()
    ratio = preview.findChild(QtWidgets.QFrame, "galleryAspectRatioDemo")
    assert ratio is not None
    assert ratio.width() >= 360
    assert ratio.height() == round(ratio.width() / (16 / 9))
    assert ratio.height() > 0
    assert ratio.layout().count() == 1
    assert ratio.layout().itemAt(0).widget().isVisible()
    window.close()


def test_gallery_tab_pane_exposes_chrome_interactions(gallery_runtime):
    app, gallery = gallery_runtime
    from shadcn_qt import TabPane

    preview = gallery.build_component_preview("TabPane")
    preview.show()
    app.processEvents()
    pane = preview.findChild(TabPane)
    assert pane is not None
    assert pane.count() == 4
    assert pane.isMovable()
    assert pane.tabsClosable()
    assert pane.documentMode()

    pane.tabCloseRequested.emit(1)
    app.processEvents()
    assert pane.count() == 3
    preview.close()


def test_gallery_exposes_stock_qtwidgets_previews(gallery_runtime):
    app, gallery = gallery_runtime
    QtWidgets = gallery.QtWidgets
    window = gallery.GalleryWindow(component="Native Forms")

    assert gallery.native_overview_names() == (
        "Native Forms",
        "Native Data Views",
        "Native Containers",
        "Native Window Chrome",
    )
    individual_names = gallery.native_individual_preview_names()
    expected_individual_count = 67 + int(hasattr(QtWidgets, "QDesktopWidget"))
    expected_individual_count += int(hasattr(QtWidgets, "QRhiWidget"))
    assert len(individual_names) == expected_individual_count
    assert len(gallery.native_preview_names()) == expected_individual_count + 4
    assert len(set(gallery.native_preview_names())) == expected_individual_count + 4

    abstract_bases = {
        "QAbstractButton",
        "QAbstractItemView",
        "QAbstractScrollArea",
        "QAbstractSlider",
        "QAbstractSpinBox",
    }
    qtwidget_subclasses = set()
    for class_name in dir(QtWidgets):
        widget_type = getattr(QtWidgets, class_name)
        if not inspect.isclass(widget_type):
            continue
        try:
            if issubclass(widget_type, QtWidgets.QWidget):
                qtwidget_subclasses.add(class_name)
        except TypeError:
            continue
    assert set(individual_names) == qtwidget_subclasses - abstract_bases
    for name in gallery.native_preview_names():
        preview = window.show_component(name)
        app.processEvents()
        assert preview.property("gallery_native_preview") is True
        assert preview.property("gallery_component") == name
        if name in individual_names:
            expected_type = getattr(QtWidgets, name)
            specimen = preview.findChild(expected_type, f"nativeGallery{name}")
            assert specimen is not None, name
            assert specimen.property("shadcn_qt_native_adopted") is True

    window.filter_components("Native QtWidgets")
    assert window.visible_component_names() == list(gallery.native_overview_names())
    window.filter_components("QLineEdit")
    assert window.visible_component_names() == ["QLineEdit"]
    window.close()


def test_native_forms_overview_places_each_control_on_its_own_row(gallery_runtime):
    app, gallery = gallery_runtime
    QtWidgets = gallery.QtWidgets
    preview = gallery.build_native_preview("Native Forms")
    preview.show()
    app.processEvents()

    controls = [
        widget
        for widget in preview.findChildren(QtWidgets.QWidget)
        if widget.property("nativeGalleryFormControl") is True
    ]
    assert len(controls) == 28
    for control in controls:
        parent_layout = control.parentWidget().layout()
        assert type(parent_layout).__name__ == "QVBoxLayout"
        assert parent_layout.indexOf(control) >= 0
    preview.close()
