import os
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

BASELINE_DIR = Path(__file__).parent / "baselines" / "native_gallery"


@pytest.fixture(scope="module")
def screenshot_runtime():
    try:
        from shadcn_qt._qt import QtCore, QtGui, QtWidgets
    except ImportError as exc:
        pytest.skip(str(exc))
    from examples.python_gallery import run as gallery

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    original_top_levels = {id(widget) for widget in app.topLevelWidgets()}
    yield app, QtCore, QtGui, gallery

    from shadcn_qt import disable_native_widget_styling

    disable_native_widget_styling(app, clear=True)
    app.processEvents()
    for widget in tuple(app.topLevelWidgets()):
        if id(widget) in original_top_levels:
            continue
        widget.close()
        widget.deleteLater()
    QtCore.QCoreApplication.sendPostedEvents(
        None,
        QtCore.QEvent.Type.DeferredDelete,
    )


def _slug(name):
    return name.casefold().replace(" ", "_")


def _smooth(QtCore):
    value = getattr(QtCore.Qt, "SmoothTransformation", None)
    if value is not None:
        return value
    return QtCore.Qt.TransformationMode.SmoothTransformation


def _ignore_aspect(QtCore):
    value = getattr(QtCore.Qt, "IgnoreAspectRatio", None)
    if value is not None:
        return value
    return QtCore.Qt.AspectRatioMode.IgnoreAspectRatio


def _perceptual_delta(actual, expected, QtCore):
    size = (122, 82)
    actual = actual.scaled(
        *size, _ignore_aspect(QtCore), _smooth(QtCore)
    )
    expected = expected.scaled(
        *size, _ignore_aspect(QtCore), _smooth(QtCore)
    )
    total = 0
    changed = 0
    for y in range(size[1]):
        for x in range(size[0]):
            left = actual.pixelColor(x, y)
            right = expected.pixelColor(x, y)
            delta = (
                abs(left.red() - right.red())
                + abs(left.green() - right.green())
                + abs(left.blue() - right.blue())
            ) / 3
            total += delta
            changed += int(delta > 28)
    pixels = size[0] * size[1]
    return total / pixels, changed / pixels


@pytest.mark.parametrize("theme", ("light", "dark"))
@pytest.mark.parametrize(
    "name",
    (
        "Native Forms",
        "Native Data Views",
        "Native Containers",
        "Native Window Chrome",
    ),
)
def test_native_gallery_matches_screenshot_baseline(
    screenshot_runtime, theme, name, tmp_path
):
    app, QtCore, QtGui, gallery = screenshot_runtime
    window = gallery.GalleryWindow(theme=theme, component=name)
    window.show()
    for _ in range(4):
        app.processEvents()
    actual = window.grab().toImage()
    window.close()
    window.deleteLater()
    app.processEvents()

    baseline_path = BASELINE_DIR / f"{theme}_{_slug(name)}.png"
    expected = QtGui.QImage(str(baseline_path))
    assert not expected.isNull(), f"Missing screenshot baseline: {baseline_path}"
    assert actual.size() == expected.size()

    mean_delta, changed_ratio = _perceptual_delta(actual, expected, QtCore)
    if mean_delta > 7.0 or changed_ratio > 0.09:
        artifact = tmp_path / baseline_path.name
        actual.save(str(artifact))
        pytest.fail(
            f"{name} ({theme}) screenshot changed: mean delta={mean_delta:.2f}, "
            f"changed pixels={changed_ratio:.1%}; actual={artifact}"
        )
