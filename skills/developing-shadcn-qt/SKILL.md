---
name: developing-shadcn-qt
description: Use when installing or releasing shadcn-qt Core, or when adding, changing, styling, documenting, previewing, or testing its Python widgets, native QtWidgets adapter, Chrome-style TabPane, Qt Designer integration, semantic tokens, QSS themes, Gallery, visual baselines, or Core/Pro boundary.
---

# Developing shadcn-qt

## Scope

Treat Python as the default implementation surface. Change C++ only when the
task explicitly requires C++ parity. Preserve the classic `new-york` geometry
and interaction profile with the Zinc light/dark palette unless the user asks
to change the project-wide visual baseline.

## Inspect Before Editing

Read the relevant section of [the repository reference](references/repository.md),
then inspect the closest implementation, its tests, and its Gallery preview.
Derive catalog and native-widget coverage from the source constants instead of
duplicating lists. The current public catalog contains 66 widgets; treat a
count change as an API change that must be reflected across exports, tests,
Designer, Gallery, and documentation.

## Route the Change

### Component API

- Preserve the closest native Qt superclass and its signals, slots, models,
  focus handling, layouts, accessibility hooks, and ownership semantics.
- Call `initialize_component(widget, "kebab-case")`. Use
  `set_choice_property` for finite values; do not call `QObject.setProperty`
  from a declared Qt property setter.
- Expose Designer properties with `qt_property`, camelCase aliases such as
  `getVariant`/`setVariant`, and `shadcnSize` instead of `size`.
- For a public widget, update `shadcn_qt.widgets.__all__`, the root lazy
  `_WIDGET_NAMES` set, Gallery coverage, component documentation, and focused
  tests. Add an explicit Designer `Spec` only for special tooltip, container,
  or initial-XML behavior.

### Visual Behavior

- Use semantic tokens and state properties. Put selector-driven styling in
  `_stylesheet.py`; use shared Qt painting helpers for shapes QSS cannot render
  reliably.
- Paint chevrons, arrows, checks, close marks, and similar UI glyphs as
  antialiased vectors. Never use Unicode or font characters as UI icons.
- Keep strokes and focus rings inside paint clips. Check first/last edges,
  focused text, hover, selected, disabled, light, and dark states.
- Keep `Tabs` as the shadcn segmented-tabs component. Keep `TabPane` and an
  opted-in native `QTabWidget` on the shared Chrome-style connected document-tab
  implementation, without replacing normal `QTabWidget` behavior.

### Native QtWidgets Compatibility

- Call `configure_high_dpi()` before constructing `QApplication` in runnable
  applications and examples. Preserve fractional Windows scale factors; never
  compensate for DPI by shrinking component geometry or QSS pixel values.
- Keep `configure`, `apply_theme`, and `enable_native_widget_styling` separate.
  Native adoption is opt-in, continuously covers later widgets, and must be
  reversible through `disable_native_widget_styling`.
- Preserve explicit user properties and the per-widget
  `shadcn_qt_native_styling=False` opt-out. Do not independently adopt Qt-owned
  embedded editors, combo views, tab bars, page stacks, or tab buttons when
  their owning complex control supplies the complete frame.
- Restore delegates, event filters, glyph overlays, shadows, popup styling,
  geometry settings, and unchanged adapter-added properties during cleanup.
- Position combo and calendar popups left-aligned immediately below their
  trigger. Give the popup one outer border; do not frame its internal view a
  second time.

### Gallery and Visual Regression

- Keep one public component or one concrete native QtWidget per detail page.
  Retain the four native family overview pages for screenshot regression.
- Preserve the one-selection Gallery color presets and their coordinated light
  and dark action, window, component-surface, border, and input overrides while
  keeping Zinc as the default baseline.
- Preserve the flat sidebar/content separator, visible branch indicators, and
  configurable single-click or double-click group expansion.
- Inspect affected previews interactively or by targeted screenshot. Update
  committed native light/dark baselines only after confirming the visual change
  is intentional.

### Tokens, Distribution, and Licensing

- Edit only `packages/design-tokens/tokens.json` for token changes, then run
  `python tools/token-codegen/generate.py`. Never hand-edit generated Python,
  QSS, or C++ token files. Run the generator after `_stylesheet.py` changes too.
- Install the public `shadcn-qt` distribution with exactly one Qt binding extra
  in a new environment. In an existing PySide/PyQt project, retain its binding
  and install without a binding extra.
- Keep Pro code, private package paths, signing keys, entitlements, and customer
  license material out of this public Core repository. The public
  `shadcn_qt.pro` module is only a compatibility bridge.

## Validate

Run focused tests first, then the applicable quality gates and visual commands
from [the repository reference](references/repository.md). Load only one Qt
binding per process and use `QT_QPA_PLATFORM=offscreen` for automated Qt tests.
For DPI changes, exercise Qt 5 and Qt 6 with a fractional 1.5 scale and verify
logical widget dimensions remain unchanged rather than rounding to 2.0.
Run `python tools/check_core_boundary.py` for boundary-related changes.

## Contribution Boundaries

Do not copy third-party source without reviewed provenance. For non-trivial
external contributions, use the exact CLA statement in `CONTRIBUTING.md`.
