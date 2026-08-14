# shadcn-qt Development Reference

## Source Map

| Change | Authoritative path | Related paths |
| --- | --- | --- |
| Semantic colors, radius, font | `packages/design-tokens/tokens.json` | `tools/token-codegen/generate.py`, `packages/python/shadcn_qt/_generated/`, `packages/cpp/shadcn_qt/include/shadcn_qt/ThemeTokens.h` |
| Python widgets | `packages/python/shadcn_qt/widgets/` | `packages/python/shadcn_qt/widgets/_helpers.py`, `packages/python/shadcn_qt/widgets/__init__.py`, `packages/python/shadcn_qt/__init__.py`, `packages/python/shadcn_qt/_stylesheet.py` |
| Vector icons and paint helpers | `packages/python/shadcn_qt/widgets/_icons.py` | `packages/python/shadcn_qt/widgets/_style.py`, `packages/python/shadcn_qt/widgets/_tab_pane.py`, `packages/python/tests/test_composite_widgets.py`, `packages/python/tests/test_new_york_style.py` |
| Themes | `packages/python/shadcn_qt/theme.py` | `packages/python/shadcn_qt/_stylesheet.py`, `packages/python/tests/test_theme.py` |
| Native Qt adoption | `packages/python/shadcn_qt/native.py` | `packages/python/tests/test_native_widgets.py`, `apps/docs/guide/native-widgets.md`, `apps/docs/guide/migration.md` |
| Qt Designer | `packages/python/shadcn_qt/designer/` | `packages/python/shadcn_qt/designer/registry.py`, `packages/python/tests/test_designer.py`, `examples/python_designer/` |
| Component tests | `packages/python/tests/test_widgets.py` | `packages/python/tests/test_composite_widgets.py`, `packages/python/tests/test_import_core.py`, `packages/python/tests/test_new_york_style.py` |
| Component Gallery | `examples/python_gallery/run.py` | `examples/python_gallery/README.md`, `packages/python/tests/test_gallery.py` |
| Native screenshots | `packages/python/tests/baselines/native_gallery/` | `tools/update_native_gallery_baselines.py`, `packages/python/tests/test_native_gallery_screenshots.py` |
| Visual contract | `docs/STYLE_BASELINE.md` | `apps/docs/components/catalog.md`, `apps/docs/components/` |
| Core/Pro boundary | `docs/PRO.md` | `packages/python/shadcn_qt/pro.py`, `tools/check_core_boundary.py` |
| Installation and release | `packages/python/pyproject.toml` | `README.md`, `packages/python/README.md`, `apps/docs/guide/install.md`, `docs/PYPI_RELEASE.md` |

## Current Catalog and Gallery Contract

- `packages/python/shadcn_qt/widgets/__init__.py::__all__` is authoritative for
  the public Python catalog. It currently exports 66 widgets in six Gallery
  groups: actions/forms, layout/disclosure, dialogs/feedback,
  navigation/menus, data/content, and conversation.
- `packages/python/shadcn_qt/__init__.py::_WIDGET_NAMES` provides root lazy
  imports. Keep it synchronized with `widgets.__all__`.
- The Designer registry derives ordinary entries from `widgets.__all__`.
  Create a manual `Spec` only for custom metadata or XML behavior.
- `examples/python_gallery/run.py::COMPONENT_CATEGORIES` must cover each public
  widget exactly once. Each component gets its own preview page.
- `NATIVE_WIDGET_CATEGORIES` and `native_individual_preview_names()` derive the
  concrete stock-Qt catalog. The count may differ by binding or Qt version
  because classes such as `QDesktopWidget` and `QRhiWidget` are conditional.
  Do not hard-code that platform-dependent count in tests or docs.
- Every individual native page must construct a discoverable instance of its
  named Qt type with object name `nativeGallery<ClassName>`. When a control such
  as `QFocusFrame` needs a host or focus target, add the supporting objects but
  keep the named target in the preview and covered by `test_gallery.py`.
- The primary PySide6 development environment currently exposes 138 Gallery
  entries: 66 Core component pages plus 72 native pages. Native pages consist
  of four family overviews and 68 individual QtWidget pages in that environment.
- Keep the four overview names stable: `Native Forms`, `Native Data Views`,
  `Native Containers`, and `Native Window Chrome`. Forms should normally place
  one control per row even on overview pages.

## Component and Qt API Rules

- Use shadcn-aligned PascalCase public classes and kebab-case component names
  for `initialize_component`.
- Preserve native Qt signals, slots, models, focus behavior, keyboard behavior,
  layouts, accessibility, parenting, and Designer serialization.
- Use `set_choice_property` for restricted values. It validates, refreshes QSS,
  and avoids recursive declared-property setters.
- Add selectors to `_stylesheet.py` only when a component needs distinct state
  styling. Run token code generation after every stylesheet or token change.
- Treat the current 66-widget count as a public-API assertion, not as a target
  to preserve by hiding intentional additions or removals.

## Visual Implementation Rules

The visual baseline is classic shadcn `new-york` geometry and interactions with
the Zinc semantic palette. `docs/STYLE_BASELINE.md` is the project contract.
Do not silently substitute the newer preset families or introduce palette
switching while fixing an individual component.

- Prefer QSS for normal box, text, hover, focus, checked, selected, invalid,
  disabled, and theme states.
- Use `_style.py`, `_icons.py`, delegates, or component painting when QSS cannot
  express the required geometry. Paint small icons as centered antialiased
  vector paths with semantic colors; never rely on platform font glyphs such as
  triangle, check, multiplication, or chevron characters.
- Inset painted borders, rings, indicators, and shadows far enough to stay
  inside the widget clip. Existing checkbox/radio indicators use a 3 px edge
  inset. Verify left edges, bottom shadows, and first/last joined controls.
- Ensure glyph hover backgrounds do not cover the parent control border. Center
  icon hit targets both horizontally and vertically.
- Give combo/list popups one outer border and a transparent, unframed internal
  view. Open popups on click release, keep them visible without holding the
  mouse, match combo width, and place them at
  `trigger.mapToGlobal(QPoint(0, trigger.height()))`. Date/calendar popups use
  the same left-aligned position but keep their natural width.
- Verify focused editors still expose a useful content rectangle; selected OTP
  digits, placeholder text, and table selection text must not be clipped or
  disappear on hover.

### Tabs versus TabPane

`Tabs` is the shadcn segmented tab control. `TabPane` is a `QTabWidget`
subclass for Chrome-style document tabs. Do not merge their visual contracts.

`TabPane` and an opted-in stock `QTabWidget` share `_tab_pane.py` painting:

- The surrounding strip is transparent.
- The active tab and page use one distinct connected surface with no gap or
  lower dividing border.
- Both lower corners grow outward curved shoulders into the page.
- Inactive hover uses the same full silhouette as the selected state.
- The first title and every close button retain uniform left/right padding.
- Close icons are vector-painted and vertically centered.
- Movable, closable, current-index, page ownership, and inherited signals and
  methods remain the normal `QTabWidget` implementation.

## Native QtWidgets Adapter Rules

Use `configure` for process defaults, `apply_theme` for application palette/QSS,
and `enable_native_widget_styling` only for opt-in adoption of existing native
widgets. Calling enable repeatedly returns the installed adapter; widgets
created later are adopted through its application event filter.

- Apply `shadcn_qt_component` and `nativeKind` only when the user did not set an
  explicit component mapping. Preserve user-set variants and other properties.
- Honor `shadcn_qt_native_styling=False`. Do not adopt existing shadcn-qt
  subclasses a second time.
- Let complex controls own their internals. In particular, do not independently
  adopt combo/spin embedded editors, combo item views, a `QTabWidget`'s tab bar
  or page stack, or tab-bar close/scroll buttons; doing so creates double
  frames, broken padding, or competing paint paths.
- Keep non-QSS enhancements reversible. Save and restore delegates, event
  filters, tab-bar options, popup style/width/name, glyph widgets, effects, and
  only those dynamic properties that still equal adapter defaults.
- Preserve system-native dialogs and platform window chrome where Qt delegates
  painting to the OS. Qt Quick/QML, web, OpenGL/RHI scenes, and third-party
  custom painting require their own theming APIs.

## Installation Guidance

The public distribution name is `shadcn-qt`; the import name is `shadcn_qt`.
The current published baseline is 0.1.0.

```bash
# New environment: choose exactly one binding extra.
python -m pip install "shadcn-qt[pyside6]"

# Existing PySide/PyQt application: retain its installed binding.
python -m pip install shadcn-qt

# Repository development.
python -m pip install -e "./packages/python[pyside6,dev]"

# Supported PySide6 Designer host.
python -m pip install "shadcn-qt[designer]"
```

Valid binding extras are `pyside6`, `pyqt6`, `pyside2`, and `pyqt5`. Never load
multiple bindings in one process. Select a binding with `SHADCN_QT_BINDING`
when required.

Core is publicly downloadable under GPL-3.0-only; proprietary use requires a
commercial Core Order Form. PyPI installation does not grant commercial rights.
Pro is separately licensed and privately distributed, not part of the public
PyPI project.

## Development and Validation

Run a focused test while iterating, then broaden validation in proportion to
the change.

```bash
# Generate and verify source-of-truth artifacts and repository boundaries.
python tools/token-codegen/generate.py
python tools/check_core_boundary.py
python tools/check_licenses.py
python tools/check_versions.py

# Full headless Python suite using the selected binding.
QT_QPA_PLATFORM=offscreen PYTHONPATH=packages/python \
  python -m pytest packages/python/tests -q

# Lint package code and the Gallery explicitly.
python -m ruff check packages/python/shadcn_qt packages/python/tests \
  examples/python_gallery/run.py tools

# Build the documentation site.
(cd apps/docs && npm ci && npm run build)
```

For interactive or screenshot inspection:

```bash
python examples/python_gallery/run.py
python examples/python_gallery/run.py --component TabPane --theme dark
python examples/python_gallery/run.py --component QTabWidget --theme light
QT_QPA_PLATFORM=offscreen python examples/python_gallery/run.py \
  --component InputOTP --screenshot /tmp/shadcn-qt-input-otp.png
```

For intentional native overview changes, inspect all four light/dark pages,
then regenerate and test the eight committed baselines:

```bash
python tools/update_native_gallery_baselines.py
QT_QPA_PLATFORM=offscreen PYTHONPATH=packages/python \
  python -m pytest packages/python/tests/test_native_gallery_screenshots.py -q
```

Useful focused tests:

- `test_widgets.py`: construction and widget properties.
- `test_composite_widgets.py`: catalog composition and the no-font-glyph rule.
- `test_new_york_style.py`: fixed geometry, state styling, popups, and TabPane.
- `test_native_widgets.py`: native coverage, ownership, popup placement, and
  reversible runtime enhancements.
- `test_gallery.py`: public/native page coverage, navigation behavior, and
  targeted preview construction.
- `test_designer.py`: Designer metadata and `.ui` reconstruction.

## Contribution Constraints

- Do not include copied third-party source without reviewed provenance and
  license records.
- Non-trivial external pull requests require this exact statement:

```text
I have read and agree to the shadcn-qt CLA v1.0: NAME, YYYY-MM-DD
```

- State that shadcn-qt is independent and not affiliated with shadcn, Vercel,
  The Qt Company, or Riverbank Computing when changing project-facing copy.
