---
name: developing-shadcn-qt
description: Use when installing shadcn-qt Core or adding or changing its Python widgets, Qt Designer integration, semantic tokens, QSS themes, Core/Pro boundaries, project tests, releases, or component documentation.
---

# Developing shadcn-qt

## Scope

Use this skill for Core installation, Python widget, token, QSS, Designer,
test, release, Core/Pro boundary, and component-documentation work. Python is
the default implementation surface; change C++ only when the task explicitly
requires C++ parity.

## Start with the Change Type

Inspect the closest existing implementation before editing.

- **Widget:** preserve the native Qt superclass, signals, slots, models, and layouts. Call `initialize_component(widget, "kebab-case")`. For finite choices, use `set_choice_property`; do not call `QObject.setProperty` from a declared Qt property setter. Expose Designer properties with `qt_property`, camelCase aliases such as `getVariant`/`setVariant`, and `shadcnSize` instead of `size`.
- **Public widget:** update `shadcn_qt.widgets` exports and the root lazy `_WIDGET_NAMES` set. Add QSS selectors in `_stylesheet.py` when the component needs distinct styling. Any `_stylesheet.py` change requires running `python tools/token-codegen/generate.py`; never hand-edit the generated outputs. The Designer registry derives ordinary entries from `widgets.__all__`; add a `Spec` only for custom tooltip, container, or default XML behavior.
- **Token:** edit only `packages/design-tokens/tokens.json`, then run `python tools/token-codegen/generate.py`. Never hand-edit `_generated/`, generated QSS, or `ThemeTokens.h`.
- **Theme or native compatibility:** preserve the boundaries between `configure`, `apply_theme`, and `enable_native_widget_styling`; retain opt-in and reversible native-widget adoption.
- **Installation:** use the public `shadcn-qt` distribution from PyPI. For a new environment, install exactly one Qt binding extra, such as `python -m pip install "shadcn-qt[pyside6]"`. For an existing PySide or PyQt project, keep its binding and install `shadcn-qt` without a binding extra. Never install several Qt binding extras or present the private Pro package as part of Core.
- **Core/Pro boundary:** keep Pro implementation, private package paths, signing keys, and customer license material out of this public repository. The public `shadcn_qt.pro` module is a compatibility bridge only. Run `python tools/check_core_boundary.py` after boundary-related changes.

## Validate

Run focused tests first, then the relevant commands in the [repository reference](references/repository.md). Use one Qt binding per process and keep tests headless with `QT_QPA_PLATFORM=offscreen` when a binding is installed.

## Contribution Boundaries

Do not copy third-party source without reviewed provenance. For non-trivial external contributions, follow the exact CLA statement in `CONTRIBUTING.md`.
