# Project status

Last verified: 2026-08-14.

## Implemented and tested

| Area | Status | Evidence |
|---|---|---|
| Python binding selection | Complete foundation | Lazy single-binding loader for PySide6, PyQt6, PySide2, and PyQt5; strict environment override |
| Python component catalog | 66 available | Qt-native mappings cover every named entry in the current shadcn/ui component index, plus Qt-specific conveniences such as `RadioButton`, `TextArea`, and the Chrome-style `TabPane` |
| Composite behavior | Available | Accordion, Collapsible, Carousel, dialogs/sheets/drawers, popovers, menus, command filtering, pagination, OTP, data tables, toast stacking, and message scrolling |
| Designer Property Editor | Available | Custom Qt properties include variants, sizes, validation, expansion, side, direction, chart type/data, typography level, and inherited Qt properties |
| Designer Widget Box | Available | Registration catalog, container metadata, DOM XML, and `shadcn-qt-designer` launcher |
| `.ui` runtime loading | Available | Unified `load_ui()` path for PyQt `uic` and PySide `QUiLoader` |
| Global themes | Available | Light/dark, semantic token overrides, radius/font overrides, custom QSS, reusable Theme objects, JSON loader |
| Existing-project compatibility | Available | QtWidgets-wide automatic styling with component/native-kind mappings, QSS plus reversible painting/delegate/glyph/elevation enhancements, dynamic coverage, scoped adoption, semantic overrides, per-widget opt-out, and cleanup |
| Token generation | Available | One renderer generates packaged Python and embedded C++ QSS |
| Python automated tests | Passing | Imports, themes, all 66 constructors, QtWidgets family coverage and reversible enhancements, composites, Gallery, Designer metadata, and real `.ui` reconstruction are covered; current full-suite result is recorded in the implementing commit |
| Designer host smoke test | Passing on macOS | `pyside6-designer` opened a custom-widget `.ui` offscreen with no registration/import errors |
| Python package | Published | Core 0.1.0 is on PyPI; wheel and sdist passed metadata/content checks, hashes matched PyPI, and the public wheel was installed and exercised with PySide6 in an isolated environment |
| Component gallery | Available | Searchable light/dark application provides interactive previews for all 66 public Core components plus four pages made only from stock QtWidgets |
| C++ foundation | Available | Button, Input, Card, CMake install package, generated QSS resources; compiled with Qt 6.9 |
| Documentation | Passing | VitePress production build succeeds |
| Visual profile | Verified | Classic `new-york` geometry and interaction states with the Zinc light/dark palette, plus Chrome-style document tabs; all 66 Gallery previews render and the core metrics are covered by automated contract tests |
| Native screenshot regression | Available | Four stock-QtWidgets Gallery pages have committed light/dark baselines (8 images) with tolerant perceptual regression tests and a reproducible update script |

## shadcn/ui alignment

The public Python catalog now provides a Qt-native class for every named component in the current shadcn/ui index. Its visual baseline is the classic `new-york` registry with the Zinc palette. Web-only implementation details are intentionally translated instead of copied: Radix DOM primitives become QWidget composition, CSS direction providers become a `Direction` container, Recharts becomes a dependency-free Qt-painted `Chart`, and typography CSS becomes a `Typography.level` property. The audited geometry and translation rules are recorded in `docs/STYLE_BASELINE.md`.

This is visual-contract and intent alignment, not a claim that different platform font rasterizers produce byte-identical browser pixels. The Qt classes retain native signals, models, focus handling, accessibility hooks, layouts, and Designer serialization while matching the new-york dimensions, semantic states, elevation hierarchy, and selection glyphs.

## Remaining hardening work

- Bring the C++ widget catalog to parity with the Python catalog.
- Add native Designer plugins for C++ consumers; the current drag/drop integration is Python-hosted and the recommended host is `pyside6-designer`.
- Run live Widget Box visibility checks on Windows and Linux and add PySide2 coverage under an older supported Python. PySide6/PyQt6/PyQt5 are covered in the current macOS verification environment.
- Add Windows/Linux baseline variants, deeper keyboard/focus conformance tests, accessibility checks, a broader optional icon pack, and wider right-to-left interaction coverage.
- Extend the basic `Chart` and `DataTable` mappings with optional high-volume/virtualized adapters without making the core package depend on QtCharts or third-party plotting libraries.
- Configure PyPI Trusted Publishing for future releases and publish signed CMake release artifacts.

These are tracked as further milestones rather than being hidden behind a claim of identical web and desktop behavior.
