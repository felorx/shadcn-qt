import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

import qt_env

BASELINE_DIR = Path(__file__).parent / "baselines" / "native_gallery"


def _platform_slug():
    """Return the baseline subdirectory for this operating system."""
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


PLATFORM = _platform_slug()


def baseline_path(theme, name):
    """Return the baseline image for ``theme``/``name``, honouring the platform.

    Platform-specific baselines live in ``baselines/native_gallery/<platform>``.
    The flat files next to that directory are the historical location recorded on
    macOS and also used by Linux CI; they stay as a fallback so those platforms
    keep working. Windows rasterizes text differently, so it never reuses them.
    """
    filename = f"{theme}_{_slug(name)}.png"
    platform_candidate = BASELINE_DIR / PLATFORM / filename
    if platform_candidate.is_file():
        return platform_candidate
    if PLATFORM == "windows":
        return platform_candidate
    legacy_candidate = BASELINE_DIR / filename
    if legacy_candidate.is_file():
        return legacy_candidate
    return platform_candidate



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
    qt_env.require_font_database("screenshot baselines record rendered text")
    baseline = baseline_path(theme, name)
    if not baseline.is_file():
        pytest.skip(
            f"no {PLATFORM} screenshot baseline for {name!r} ({theme}); "
            "regenerate with tools/update_native_gallery_baselines.py"
        )
    window = gallery.GalleryWindow(theme=theme, component=name)
    window.show()
    for _ in range(4):
        app.processEvents()
    actual = window.grab().toImage()
    window.close()
    window.deleteLater()
    app.processEvents()

    expected = QtGui.QImage(str(baseline))
    assert not expected.isNull(), f"Missing screenshot baseline: {baseline}"
    assert actual.size() == expected.size(), (
        f"{name} ({theme}) captured {actual.width()}x{actual.height()} but the "
        f"{PLATFORM} baseline is {expected.width()}x{expected.height()}"
    )

    mean_delta, changed_ratio = _perceptual_delta(actual, expected, QtCore)
    if mean_delta > 7.0 or changed_ratio > 0.09:
        artifact = tmp_path / baseline.name
        actual.save(str(artifact))
        pytest.fail(
            f"{name} ({theme}) screenshot changed: mean delta={mean_delta:.2f}, "
            f"changed pixels={changed_ratio:.1%}; actual={artifact}"
        )
