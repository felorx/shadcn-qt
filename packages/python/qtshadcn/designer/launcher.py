"""Launch the matching Qt Designer with qtshadcn plugins enabled."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Union

from qtshadcn import _qt


def designer_plugin_path() -> Path:
    return Path(__file__).resolve().parent / "plugins"


def _prepend_path(value: str, current: Optional[str]) -> str:
    parts = [part for part in (current or "").split(os.pathsep) if part]
    return os.pathsep.join([value] + [part for part in parts if part != value])


def designer_environment(base: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
    """Return an environment suitable for PySide and PyQt Designer loaders."""

    env = dict(os.environ if base is None else base)
    plugin_dir = str(designer_plugin_path())
    # pyside6-designer embeds Python and does not always inherit the launching
    # virtual environment's site-packages.  Make the package root explicit.
    package_parent = str(Path(__file__).resolve().parents[2])
    env["PYTHONPATH"] = _prepend_path(package_parent, env.get("PYTHONPATH"))
    env["PYSIDE_DESIGNER_PLUGINS"] = _prepend_path(
        plugin_dir, env.get("PYSIDE_DESIGNER_PLUGINS")
    )
    env["PYQTDESIGNERPATH"] = _prepend_path(plugin_dir, env.get("PYQTDESIGNERPATH"))
    env.setdefault("QTSHADCN_QT_BINDING", _qt.detect_binding())
    env.setdefault("QTSHADCN_DESIGNER_THEME", "light")
    return env


def _binary_candidates(binding: str) -> Iterable[Path]:
    explicit = os.environ.get("QTSHADCN_DESIGNER")
    if explicit:
        yield Path(explicit).expanduser()

    script_name = "pyside6-designer" if binding == "PySide6" else "pyside2-designer"
    if binding.startswith("PySide"):
        yield Path(sys.executable).parent / (
            f"{script_name}.exe" if sys.platform == "win32" else script_name
        )
        found = shutil.which(script_name)
        if found:
            yield Path(found)

    core, _, _ = _qt.qt_modules()
    info = core.QLibraryInfo
    binaries_key = getattr(info, "BinariesPath", None)
    if binaries_key is None:
        binaries_key = info.LibraryPath.BinariesPath
    location_fn = getattr(info, "path", None) or getattr(info, "location")
    binary_dir = Path(location_fn(binaries_key))
    yield binary_dir / ("designer.exe" if sys.platform == "win32" else "designer")
    if sys.platform == "darwin":
        yield binary_dir / "Designer.app" / "Contents" / "MacOS" / "Designer"

    found = shutil.which("designer")
    if found:
        yield Path(found)


UnionPath = Union[str, Path]


def designer_command(executable: Optional[UnionPath] = None) -> List[str]:
    """Resolve a Designer executable compatible with the active binding."""

    _qt.detect_binding()
    candidates = (
        [Path(executable).expanduser()]
        if executable
        else list(_binary_candidates(_qt.detect_binding()))
    )
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return [str(candidate)]
    searched = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(
        "No Qt Designer executable was found. Install the binding's Designer "
        "tool (PySide6 users can run `pyside6-designer`) or set "
        f"QTSHADCN_DESIGNER. Searched: {searched}"
    )


def launch_designer(
    arguments: Optional[Iterable[str]] = None,
    *,
    executable: Optional[UnionPath] = None,
) -> int:
    """Start Designer and wait for it to exit."""

    command = designer_command(executable) + list(arguments or ())
    return subprocess.call(command, env=designer_environment())


def main(argv: Optional[List[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args == ["--print-plugin-path"]:
        print(designer_plugin_path())
        return 0
    if args == ["--print-command"]:
        print(" ".join(designer_command()))
        return 0
    return launch_designer(args)


if __name__ == "__main__":
    raise SystemExit(main())
