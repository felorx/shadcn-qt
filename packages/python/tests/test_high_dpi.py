import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

import qt_env


def test_qt5_defaults_enable_scaling_and_preserve_fractional_dpr():
    from shadcn_qt._qt import _configure_high_dpi_defaults

    class ApplicationAttribute:
        AA_EnableHighDpiScaling = 1
        AA_UseHighDpiPixmaps = 2

    class RoundingPolicy:
        PassThrough = 5

    qt = SimpleNamespace(
        ApplicationAttribute=ApplicationAttribute,
        HighDpiScaleFactorRoundingPolicy=RoundingPolicy,
    )

    class QCoreApplication:
        attributes = []

        @staticmethod
        def instance():
            return None

        @classmethod
        def setAttribute(cls, attribute, enabled):
            cls.attributes.append((attribute, enabled))

    class QGuiApplication:
        policy = None

        @classmethod
        def setHighDpiScaleFactorRoundingPolicy(cls, policy):
            cls.policy = policy

    core = SimpleNamespace(
        Qt=qt,
        QCoreApplication=QCoreApplication,
        qVersion=lambda: "5.15.19",
    )
    gui = SimpleNamespace(QGuiApplication=QGuiApplication)

    assert _configure_high_dpi_defaults(core, gui)
    assert QCoreApplication.attributes == [(1, True), (2, True)]
    assert QGuiApplication.policy == RoundingPolicy.PassThrough


def test_qt6_defaults_leave_scaling_enabled_and_preserve_fractional_dpr():
    from shadcn_qt._qt import _configure_high_dpi_defaults

    class RoundingPolicy:
        PassThrough = 5

    qt = SimpleNamespace(HighDpiScaleFactorRoundingPolicy=RoundingPolicy)

    class QCoreApplication:
        attributes = []

        @staticmethod
        def instance():
            return None

        @classmethod
        def setAttribute(cls, attribute, enabled):
            cls.attributes.append((attribute, enabled))

    class QGuiApplication:
        policy = None

        @classmethod
        def setHighDpiScaleFactorRoundingPolicy(cls, policy):
            cls.policy = policy

    core = SimpleNamespace(
        Qt=qt,
        QCoreApplication=QCoreApplication,
        qVersion=lambda: "6.11.1",
    )
    gui = SimpleNamespace(QGuiApplication=QGuiApplication)

    assert _configure_high_dpi_defaults(core, gui)
    assert QCoreApplication.attributes == []
    assert QGuiApplication.policy == RoundingPolicy.PassThrough


def test_fractional_scale_stays_fractional_in_real_qt_process():
    qt_env.require_qt_binding()
    package_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["QT_SCALE_FACTOR"] = "1.5"
    env["PYTHONPATH"] = os.pathsep.join(
        part
        for part in (str(package_root), env.get("PYTHONPATH", ""))
        if part
    )
    script = """
from shadcn_qt import Button, configure_high_dpi
from shadcn_qt._qt import QtCore, QtGui, QtWidgets

policy = getattr(
    getattr(QtCore.Qt, "HighDpiScaleFactorRoundingPolicy"),
    "PassThrough",
)
assert QtGui.QGuiApplication.highDpiScaleFactorRoundingPolicy() == policy
configure_high_dpi()
assert QtGui.QGuiApplication.highDpiScaleFactorRoundingPolicy() == policy
app = QtWidgets.QApplication([])
button = Button("DPI")
button.show()
app.processEvents()
assert button.height() == 36
dpr = button.devicePixelRatioF()
assert abs(dpr - 1.5) <= 0.1
assert button.grab().devicePixelRatio() == dpr

try:
    configure_high_dpi()
except RuntimeError as exc:
    assert "before creating QApplication" in str(exc)
else:
    raise AssertionError("late DPI configuration must fail explicitly")
"""
    completed = subprocess.run(
        [sys.executable, "-c", script],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        pytest.fail(
            "high-DPI subprocess failed\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
