#!/usr/bin/env python3
"""Regenerate the native QtWidgets Gallery screenshot baselines."""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from shadcn_qt._qt import QtWidgets  # noqa: E402

from examples.python_gallery import run as gallery  # noqa: E402

BASELINE_DIR = ROOT / "packages" / "python" / "tests" / "baselines" / "native_gallery"


def _slug(name: str) -> str:
    return name.casefold().replace(" ", "_")


def main() -> int:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    BASELINE_DIR.mkdir(parents=True, exist_ok=True)
    for theme in ("light", "dark"):
        for name in gallery.native_overview_names():
            window = gallery.GalleryWindow(theme=theme, component=name)
            window.show()
            for _ in range(4):
                app.processEvents()
            target = BASELINE_DIR / f"{theme}_{_slug(name)}.png"
            if not window.save_screenshot(target):
                raise RuntimeError(f"Could not save screenshot to {target}")
            window.close()
            window.deleteLater()
            app.processEvents()
            print(target.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
