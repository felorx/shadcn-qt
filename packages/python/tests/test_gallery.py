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
