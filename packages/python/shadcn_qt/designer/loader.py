"""Load Qt Designer ``.ui`` files under any supported Python binding."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Optional, Union

from shadcn_qt import _qt


def load_ui(path: Union[str, Path], parent: Optional[Any] = None) -> Any:
    """Load a ``.ui`` file containing shadcn-qt custom widgets.

    PyQt uses its native ``uic.loadUi`` implementation.  PySide uses
    ``QUiLoader`` after registering every shadcn-qt widget class.
    """

    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    binding = _qt.detect_binding()

    if binding.startswith("PyQt"):
        uic = importlib.import_module(f"{binding}.uic")
        return uic.loadUi(str(source), parent)

    core, _, _ = _qt.qt_modules()
    ui_tools = _qt.import_qt_module("QtUiTools")
    loader = ui_tools.QUiLoader()
    from shadcn_qt import widgets as widget_module

    for name in widget_module.__all__:
        loader.registerCustomWidget(getattr(widget_module, name))

    device = core.QFile(str(source))
    read_only = getattr(core.QIODevice, "ReadOnly", None)
    if read_only is None:
        read_only = core.QIODevice.OpenModeFlag.ReadOnly
    if not device.open(read_only):
        raise OSError(f"Unable to open UI file: {source}")
    try:
        widget = loader.load(device, parent)
    finally:
        device.close()
    if widget is None:
        raise RuntimeError(loader.errorString() or f"Unable to load {source}")
    return widget


__all__ = ["load_ui"]
