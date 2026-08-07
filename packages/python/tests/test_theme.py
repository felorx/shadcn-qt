import json

import pytest

from qtshadcn.theme import (
    Theme,
    available_themes,
    create_theme,
    load_theme,
    resolve_theme,
    theme_stylesheet,
)


def test_builtin_and_overridden_theme():
    assert set(available_themes()) >= {"light", "dark"}
    brand = create_theme(
        "brand",
        base="dark",
        colors={"primary": "#7c3aed"},
        radius={"md": "10px"},
    )
    assert isinstance(brand, Theme)
    assert brand.colors["primary"] == "#7c3aed"
    assert brand.colors["background"] == resolve_theme("dark").colors["background"]
    assert "#7c3aed" in theme_stylesheet(brand)


def test_load_json_theme(tmp_path):
    path = tmp_path / "ocean.json"
    path.write_text(
        json.dumps(
            {
                "base": "light",
                "colors": {"primary": "#0369a1", "ring": "#0ea5e9"},
                "radius": {"md": "12px"},
            }
        ),
        encoding="utf-8",
    )
    theme = load_theme(path)
    assert theme.name == "ocean"
    assert theme.colors["primary"] == "#0369a1"
    assert theme.radius["md"] == "12px"


def test_incomplete_theme_is_rejected():
    with pytest.raises(ValueError, match="missing colors"):
        Theme("broken", {"background": "#fff"})
