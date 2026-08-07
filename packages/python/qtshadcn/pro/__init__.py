"""
Pro-only extensions (commercial distribution).

The open-source package does not ship Pro modules. Importing ``qtshadcn.pro`` will fail
with instructions to obtain a Pro build.
"""

from __future__ import annotations

raise ImportError(
    "qtshadcn.pro is not included in the Community edition. "
    "See docs/TIERS.md for Pro scope and licensing."
)
