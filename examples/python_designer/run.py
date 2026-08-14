#!/usr/bin/env python3
"""Load a Designer-authored form without generating Python code first."""

from pathlib import Path

from shadcn_qt import apply_theme, app_exec, configure_high_dpi
from shadcn_qt._qt import QtWidgets
from shadcn_qt.designer import load_ui


def main() -> None:
    configure_high_dpi()
    app = QtWidgets.QApplication([])
    apply_theme(app, "light")
    form = load_ui(Path(__file__).with_name("form.ui"))
    form.show()
    app_exec(app)


if __name__ == "__main__":
    main()
