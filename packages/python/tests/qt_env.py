"""Environment probes shared by the test modules.

Some assertions describe the host Qt platform rather than shadcn-qt: they
encode font metrics or screenshot pixels.  A machine without a font database
(the ``offscreen`` plugin on Windows, ``minimal`` anywhere) cannot evaluate
them, and CI installs the package without a Qt binding on purpose to prove the
degraded import path works.  The helpers below let a test skip instead of
failing when the property under test cannot be observed.
"""

import pytest


def qt_binding_available():
    """Return whether one of the supported Qt bindings can actually load."""
    try:
        from shadcn_qt._qt import QtWidgets  # noqa: F401
    except ImportError:
        return False
    return True


def require_qt_binding():
    """Skip the calling test when no Qt binding is installed."""
    if not qt_binding_available():
        pytest.skip("no Qt binding installed")


def font_family_count():
    """Return the number of font families the current platform exposes."""
    try:
        from shadcn_qt._qt import QtGui
    except ImportError:
        return 0

    database = getattr(QtGui, "QFontDatabase", None)
    if database is None:
        return 0

    # PySide6 and PyQt6 expose ``families`` as a static method, Qt5 bindings
    # only on an instance.
    for accessor in (database.families, lambda: database().families()):
        try:
            return len(accessor())
        except Exception:
            continue
    return 0


def require_font_database(reason):
    """Skip the calling test when the platform has no usable font database."""
    if font_family_count() == 0:
        pytest.skip(f"Qt platform exposes no fonts ({reason})")


def qt_major_version():
    """Return the Qt major version in use, or 0 when Qt is unavailable."""
    try:
        from shadcn_qt._qt import QtCore
    except ImportError:
        return 0
    try:
        return int(QtCore.qVersion().split(".", 1)[0])
    except (AttributeError, TypeError, ValueError):
        return 0


def qpa_platform_name():
    """Return the active QPA platform plugin name, or an empty string."""
    try:
        from shadcn_qt._qt import QtGui
    except ImportError:
        return ""
    app = QtGui.QGuiApplication.instance()
    if app is None:
        return ""
    try:
        return app.platformName()
    except (AttributeError, TypeError):
        return ""


def require_offscreen_dialog_support(reason):
    """Skip Qt 5 dialog tests on the ``offscreen`` plugin.

    Qt 5.15 for Python crashes with an access violation when a
    ``QMessageBox`` that owns standard buttons is shown through the
    ``offscreen`` platform plugin.  A bare PyQt5 script with no shadcn-qt code
    reproduces it, so the assertions below cannot observe anything on that
    combination.  Real desktop platforms and Qt 6 are unaffected.
    """
    if qt_major_version() == 5 and qpa_platform_name() == "offscreen":
        pytest.skip(f"Qt 5 offscreen crashes when showing a QMessageBox ({reason})")
