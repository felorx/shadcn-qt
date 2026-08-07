# Project status

Last verified: 2026-08-08.

## Implemented and tested

| Area | Status | Evidence |
|---|---|---|
| Python binding selection | Complete foundation | Lazy single-binding loader for PySide6, PyQt6, PySide2, and PyQt5; strict environment override |
| Python component catalog | 65 available | Qt-native mappings cover every named entry in the current shadcn/ui component index, plus Qt-specific conveniences such as `RadioButton` and `TextArea` |
| Composite behavior | Available | Accordion, Collapsible, Carousel, dialogs/sheets/drawers, popovers, menus, command filtering, pagination, OTP, data tables, toast stacking, and message scrolling |
| Designer Property Editor | Available | Custom Qt properties include variants, sizes, validation, expansion, side, direction, chart type/data, typography level, and inherited Qt properties |
| Designer Widget Box | Available | Registration catalog, container metadata, DOM XML, and `qtshadcn-designer` launcher |
| `.ui` runtime loading | Available | Unified `load_ui()` path for PyQt `uic` and PySide `QUiLoader` |
| Global themes | Available | Light/dark, semantic token overrides, radius/font overrides, custom QSS, reusable Theme objects, JSON loader |
| Token generation | Available | One renderer generates packaged Python and embedded C++ QSS |
| Python automated tests | Passing | 15/15 under PySide6 6.11, PyQt6 6.11, and PyQt5 5.15: imports, themes, all 65 constructors, composite behavior, Designer metadata, and real `.ui` reconstruction |
| Designer host smoke test | Passing on macOS | `pyside6-designer` opened a custom-widget `.ui` offscreen with no registration/import errors |
| Python wheel | Passing | Built wheel, inspected packaged plugin/QSS contents, and loaded a Designer form from a clean target install |
| C++ foundation | Available | Button, Input, Card, CMake install package, generated QSS resources; compiled with Qt 6.9 |
| Documentation | Passing | VitePress production build succeeds |

## shadcn/ui alignment

The public Python catalog now provides a Qt-native class for every named component in the current shadcn/ui index. Web-only implementation details are intentionally translated instead of copied: Radix DOM primitives become QWidget composition, CSS direction providers become a `Direction` container, Recharts becomes a dependency-free Qt-painted `Chart`, and typography CSS becomes a `Typography.level` property.

This is catalog and intent alignment, not a claim that Qt widgets have byte-for-byte React/Radix behavior. The Qt classes retain native signals, models, focus handling, accessibility hooks, layouts, and Designer serialization.

## Remaining hardening work

- Bring the C++ widget catalog to parity with the Python catalog.
- Add native Designer plugins for C++ consumers; the current drag/drop integration is Python-hosted and the recommended host is `pyside6-designer`.
- Run live Widget Box visibility checks on Windows and Linux and add PySide2 coverage under an older supported Python. PySide6/PyQt6/PyQt5 are covered in the current macOS verification environment.
- Add visual regression snapshots, deeper keyboard/focus conformance tests, accessibility checks, icon packs, and broader right-to-left interaction coverage.
- Extend the basic `Chart` and `DataTable` mappings with optional high-volume/virtualized adapters without making the core package depend on QtCharts or third-party plotting libraries.
- Add CI matrices and publish signed PyPI/CMake release artifacts.

These are tracked as further milestones rather than being hidden behind a claim of identical web and desktop behavior.
