#!/usr/bin/env python3
"""Minimal demo using PyQt5."""

import os

os.environ.setdefault("SHADCN_QT_BINDING", "PyQt5")

from shadcn_qt import Button, Card, Input, apply_theme, app_exec
from shadcn_qt._qt import QtWidgets


def main() -> None:
    app = QtWidgets.QApplication([])
    apply_theme(app, "dark")

    w = QtWidgets.QWidget()
    w.setWindowTitle("shadcn-qt — PyQt5 (dark)")
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
    row.addWidget(Button("Destructive", card, variant="destructive"))
    lay.addLayout(row)

    root.addWidget(card)
    w.resize(420, 280)
    w.show()
    app_exec(app)


if __name__ == "__main__":
    main()
