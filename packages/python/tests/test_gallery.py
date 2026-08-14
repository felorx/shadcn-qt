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

    assert len(gallery.component_names()) == 65
    assert len(set(gallery.component_names())) == 65
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
    window.filter_components("message")
    assert window.visible_component_names() == ["Message", "MessageScroller"]

    window.set_theme("dark")
    assert app.property("shadcn_qt_gallery_theme") == "dark"
    assert window.theme_select.currentText() == "Dark"
    window.close()


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


def test_gallery_exposes_stock_qtwidgets_previews(gallery_runtime):
    app, gallery = gallery_runtime
    window = gallery.GalleryWindow(component="Native Forms")

    assert gallery.native_preview_names() == (
        "Native Forms",
        "Native Data Views",
        "Native Containers",
        "Native Window Chrome",
    )
    for name in gallery.native_preview_names():
        preview = window.show_component(name)
        app.processEvents()
        assert preview.property("gallery_native_preview") is True
        assert preview.property("gallery_component") == name

    window.filter_components("Native QtWidgets")
    assert window.visible_component_names() == list(gallery.native_preview_names())
    window.close()
