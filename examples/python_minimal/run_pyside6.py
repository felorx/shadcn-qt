#!/usr/bin/env python3
"""Minimal demo using PySide6 (install: pip install -e '.[pyside6]' from packages/python)."""

import os

os.environ.setdefault("QTSHADCN_QT_BINDING", "PySide6")

from qtshadcn import Button, Card, Input, apply_theme, app_exec
from qtshadcn._qt import QtWidgets


def main() -> None:
    app = QtWidgets.QApplication([])
    apply_theme(app, "light")

    w = QtWidgets.QWidget()
    w.setWindowTitle("qtshadcn — PySide6")
    root = QtWidgets.QVBoxLayout(w)

    card = Card(w)
    lay = QtWidgets.QVBoxLayout(card)
    lay.setContentsMargins(24, 24, 24, 24)
    lay.setSpacing(12)
    lay.addWidget(QtWidgets.QLabel("Card + Button + Input", card))
    inp = Input(card)
    inp.setPlaceholderText("Email")
    lay.addWidget(inp)
    row = QtWidgets.QHBoxLayout()
    row.addWidget(Button("Primary", card, variant="default"))
    row.addWidget(Button("Outline", card, variant="outline"))
    lay.addLayout(row)

    root.addWidget(card)
    w.resize(420, 280)
    w.show()
    app_exec(app)


if __name__ == "__main__":
    main()
