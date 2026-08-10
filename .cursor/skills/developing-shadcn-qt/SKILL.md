---
name: developing-shadcn-qt
description: Use when adding or changing shadcn-qt Python widgets, Qt Designer integration, semantic tokens, QSS themes, project tests, or component documentation in this repository.
---

# Developing shadcn-qt

## Scope

Use this skill for core Python widget, token, QSS, Designer, test, and component-documentation work. Python is the default implementation surface; change C++ only when the task explicitly requires C++ parity.

## Start with the Change Type

Inspect the closest existing implementation before editing.

- **Widget:** preserve the native Qt superclass, signals, slots, models, and layouts. Call `initialize_component(widget, "kebab-case")`. For finite choices, use `set_choice_property`; do not call `QObject.setProperty` from a declared Qt property setter. Expose Designer properties with `qt_property`, camelCase aliases such as `getVariant`/`setVariant`, and `shadcnSize` instead of `size`.
- **Public widget:** update `shadcn_qt.widgets` exports and the root lazy `_WIDGET_NAMES` set. Add QSS selectors in `_stylesheet.py` when the component needs distinct styling. Any `_stylesheet.py` change requires running `python tools/token-codegen/generate.py`; never hand-edit the generated outputs. The Designer registry derives ordinary entries from `widgets.__all__`; add a `Spec` only for custom tooltip, container, or default XML behavior.
- **Token:** edit only `packages/design-tokens/tokens.json`, then run `python tools/token-codegen/generate.py`. Never hand-edit `_generated/`, generated QSS, or `ThemeTokens.h`.
- **Theme or native compatibility:** preserve the boundaries between `configure`, `apply_theme`, and `enable_native_widget_styling`; retain opt-in and reversible native-widget adoption.

## Validate

Run focused tests first, then the relevant commands in [reference.md](reference.md). Use one Qt binding per process and keep tests headless with `QT_QPA_PLATFORM=offscreen` when a binding is installed.

## Contribution Boundaries

Do not copy third-party source without reviewed provenance. For non-trivial external contributions, follow the exact CLA statement in `CONTRIBUTING.md`.
