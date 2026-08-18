import json

import pytest

from shadcn_qt.theme import (
    Theme,
    ThemeConfig,
    available_themes,
    configure,
    create_theme,
    current_theme,
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


def test_radius_base_derives_all_semantic_sizes_and_allows_explicit_overrides():
    rounded = create_theme(
        "rounded",
        radius_base=9,
        radius={"xl": "20px"},
    )

    assert rounded.radius == {
        "sm": "6px",
        "md": "9px",
        "lg": "12px",
        "xl": "20px",
    }
    qss = theme_stylesheet("light", radius_base="9px")
    assert "border-radius: 6px" in qss
    assert "border-radius: 9px" in qss
    assert "border-radius: 12px" in qss
    assert "border-radius: 18px" in qss


def test_configure_accepts_one_process_wide_radius_value(monkeypatch):
    from shadcn_qt import theme as theme_module

    monkeypatch.setattr(theme_module, "_CONFIG", ThemeConfig())
    configure(radius_base="12px", radius={"xl": "30px"})

    assert current_theme().radius == {
        "sm": "8px",
        "md": "12px",
        "lg": "16px",
        "xl": "30px",
    }


@pytest.mark.parametrize("value", [-1, float("inf"), "1rem", True])
def test_radius_base_rejects_invalid_values(value):
    with pytest.raises((TypeError, ValueError), match="radius_base"):
        create_theme("invalid-radius", radius_base=value)


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


def test_load_json_theme_accepts_radius_base(tmp_path):
    path = tmp_path / "rounded.json"
    path.write_text(
        json.dumps({"base": "light", "radiusBase": 12}),
        encoding="utf-8",
    )

    theme = load_theme(path)

    assert theme.radius == {
        "sm": "8px",
        "md": "12px",
        "lg": "16px",
        "xl": "24px",
    }


def test_incomplete_theme_is_rejected():
    with pytest.raises(ValueError, match="missing colors"):
        Theme("broken", {"background": "#fff"})
