"""Shared helpers for deriving and consuming semantic corner radii."""

from __future__ import annotations

import math
import re
from typing import Dict, Union


RadiusBase = Union[int, float, str]

_RADIUS_RATIOS = {
    "sm": 2.0 / 3.0,
    "md": 1.0,
    "lg": 4.0 / 3.0,
    "xl": 2.0,
}
_PX_VALUE = re.compile(r"^[+]?(?:\d+(?:\.\d*)?|\.\d+)\s*(?:px)?$", re.I)


def radius_pixels(value: RadiusBase, *, name: str = "radius_base") -> float:
    """Return a non-negative pixel value accepted by Qt Style Sheets."""

    if isinstance(value, bool):
        raise TypeError(f"{name} must be a number or '<number>px', not bool")
    if isinstance(value, (int, float)):
        result = float(value)
    elif isinstance(value, str):
        raw = value.strip()
        if not _PX_VALUE.fullmatch(raw):
            raise ValueError(f"{name} must be a non-negative pixel value")
        result = float(re.sub(r"px$", "", raw, flags=re.I).strip())
    else:
        raise TypeError(f"{name} must be a number or '<number>px'")
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{name} must be a finite non-negative pixel value")
    return result


def format_radius(value: float) -> str:
    """Format a pixel radius compactly while preserving derived proportions."""

    formatted = f"{value:.3f}".rstrip("0").rstrip(".")
    return f"{formatted or '0'}px"


def derive_radius(radius_base: RadiusBase) -> Dict[str, str]:
    """Derive the sm/md/lg/xl family from one md-sized base radius."""

    base = radius_pixels(radius_base)
    return {
        name: format_radius(base * ratio)
        for name, ratio in _RADIUS_RATIOS.items()
    }


__all__ = ["RadiusBase", "derive_radius", "format_radius", "radius_pixels"]
