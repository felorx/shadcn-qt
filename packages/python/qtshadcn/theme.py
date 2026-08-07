"""Apply generated QSS themes to QApplication."""

from __future__ import annotations

from typing import Literal, Optional

from qtshadcn._generated.base_qss import DARK_QSS, LIGHT_QSS
from qtshadcn._qt import QtGui, QtWidgets, detect_binding

ThemeMode = Literal["light", "dark"]


def apply_theme(app: Optional[QtWidgets.QApplication], mode: ThemeMode = "light") -> None:
    """Set application stylesheet to the generated light or dark theme."""
    detect_binding()
    if app is None:
        app = QtWidgets.QApplication.instance()
    if app is None:
        raise RuntimeError("No QApplication instance; create QApplication before apply_theme.")
    app.setStyleSheet(DARK_QSS if mode == "dark" else LIGHT_QSS)


def apply_palette_from_tokens(
    app: QtWidgets.QApplication,
    mode: ThemeMode = "light",
) -> None:
    """Optional: set QPalette basics from generated semantic colors (supplements QSS)."""
    from qtshadcn._generated.colors import THEMES

    detect_binding()
    t = THEMES[mode]
    def _role(name: str):
        P = QtGui.QPalette
        return getattr(P, name) if hasattr(P, name) else getattr(P.ColorRole, name)

    pal = QtGui.QPalette()
    bg = QtGui.QColor(t["background"])
    fg = QtGui.QColor(t["foreground"])
    pal.setColor(_role("Window"), bg)
    pal.setColor(_role("WindowText"), fg)
    pal.setColor(_role("Base"), bg)
    pal.setColor(_role("Text"), fg)
    pal.setColor(_role("Button"), QtGui.QColor(t["secondary"]))
    pal.setColor(_role("ButtonText"), fg)
    app.setPalette(pal)
