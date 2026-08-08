"""shadcn-qt registration entry point executed by Qt Designer."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Qt for Python executes register scripts without defining __file__, and its
# embedded interpreter may omit the launcher's site-packages.  Recover the
# package parent from either registration-path environment variable.
for _variable in ("PYSIDE_DESIGNER_PLUGINS", "PYQTDESIGNERPATH"):
    for _entry in os.environ.get(_variable, "").split(os.pathsep):
        if _entry:
            _candidate = Path(_entry).expanduser().resolve()
            if _candidate.name == "plugins" and len(_candidate.parents) >= 3:
                _package_parent = str(_candidate.parents[2])
                if _package_parent not in sys.path:
                    sys.path.insert(0, _package_parent)

from shadcn_qt.designer.registry import *  # noqa: E402,F403


if __name__ == "__main__":
    register_pyside_widgets()  # noqa: F405
