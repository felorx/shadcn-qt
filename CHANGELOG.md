# Changelog

All notable changes to shadcn-qt Core are documented here. The project follows
[Semantic Versioning](https://semver.org/).

## 0.2.2 - 2026-08-15

### Added

- Added one-click Zinc, Blue, Violet, Emerald, Orange, and Rose color presets
  to the Gallery, with coordinated light/dark window, component-surface,
  action, input, border, and focus colors.
- Added the Gallery `--color-theme` option for launching directly into a
  color preset.

### Changed

- Tightened adopted `QGroupBox` spacing so its title and content share the
  same left alignment while retaining a compact frame inset.
- Updated the Gallery, theming documentation, native screenshot baselines,
  and the `developing-shadcn-qt` AI skill for the new visual contracts.

### Fixed

- Removed the inner rounded focus rectangle around selected `TabPane` and
  adopted `QTabWidget` titles; keyboard focus now follows the outer Chrome-style
  tab silhouette.

## 0.2.1 - 2026-08-15

### Added

- Added `configure_high_dpi()` as a public pre-`QApplication` initializer for
  consistent fractional scaling across PySide6, PyQt6, PySide2, and PyQt5.

### Changed

- Updated the Gallery, runnable examples, developer documentation, and the
  `developing-shadcn-qt` AI skill with the high-DPI startup contract.

### Fixed

- Preserved Windows 125%, 150%, and 175% display scales instead of allowing
  Qt 5 to round fractional scale factors to an oversized integer scale.
- Kept the selected `TabPane` and adopted `QTabWidget` page background
  connected to the active tab title in light and dark themes.

## 0.2.0 - 2026-08-15

### Added

- A searchable light/dark Gallery with dedicated previews for all 66 public
  Core components and the concrete native QtWidgets catalog.
- Opt-in, continuously applied, and reversible styling for existing QtWidgets
  applications, including forms, data views, containers, window chrome, and
  dialogs.
- Four stock-QtWidgets overview pages with eight committed light/dark screenshot
  baselines and perceptual regression tests.
- A Chrome-style `TabPane` component, with the same connected document-tab
  treatment available to adopted native `QTabWidget` instances.
- A standalone `developing-shadcn-qt` AI skill and installation guidance for
  Codex, Cursor, and other compatible agents.

### Changed

- Aligned the complete component catalog with the classic shadcn `new-york`
  geometry and interaction profile using the Zinc light/dark palette.
- Replaced font-backed UI symbols with centered, antialiased vector glyphs.
- Expanded the Gallery so native form and container controls can be inspected
  on individual pages while retaining the family overview pages.
- Made Gallery navigation group expansion configurable between single-click
  and double-click operation.

### Fixed

- Corrected clipped borders, focus rings, selected text, OTP sizing, popup
  placement, duplicate popup frames, and hover/selection contrast.
- Corrected combo-box press/release behavior so popup panels remain open after
  a normal click.
- Corrected arrow, close-button, calendar, toast, item-action, spin-box, and
  other glyph alignment across custom and native components.
- Prevented Qt-owned embedded editors, popup views, tab bars, page stacks, and
  tab buttons from receiving competing native frames or paint paths.

## 0.1.0 - 2026-08-14

- Initial public PyPI release of shadcn-qt Core with Python binding selection,
  semantic tokens, the 65-component baseline catalog, Qt Designer integration,
  C++ foundations, and GPL/commercial dual licensing.
