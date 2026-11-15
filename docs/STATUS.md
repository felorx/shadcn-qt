# Project status

Last verified: 2026-11-16.

## Implemented and tested

| Area | Status | Evidence |
|---|---|---|
| Python binding selection | Complete foundation | Lazy single-binding loader for PySide6, PyQt6, PySide2, and PyQt5; strict environment override that accepts any letter case |
| Python component catalog | 66 available | Qt-native mappings cover every named entry in the current shadcn/ui component index, plus Qt-specific conveniences such as `RadioButton`, `TextArea`, and the Chrome-style `TabPane` |
| Composite behavior | Available | Accordion, Collapsible, Carousel, dialogs/sheets/drawers, popovers, menus, command filtering, pagination, OTP, data tables, toast stacking, and message scrolling |
| Designer Property Editor | Available | Custom Qt properties include variants, sizes, validation, expansion, side, direction, chart type/data, typography level, and inherited Qt properties |
| Designer Widget Box | Available | Registration catalog, container metadata, DOM XML, and `shadcn-qt-designer` launcher |
| `.ui` runtime loading | Available | Unified `load_ui()` path for PyQt `uic` and PySide `QUiLoader` |
| Global themes | Available | Light/dark, one-value proportional radius scaling, semantic token overrides, font overrides, custom QSS, reusable Theme objects, JSON loader |
| Existing-project compatibility | Available | QtWidgets-wide automatic styling with component/native-kind mappings, QSS plus reversible painting/delegate/glyph/elevation enhancements, dynamic coverage, scoped adoption, semantic overrides, per-widget opt-out, and cleanup |
| Token generation | Available | One renderer generates packaged Python and embedded C++ QSS; CI fails when the committed output differs from a fresh run |
| Python automated tests | Passing | Imports, themes, all 66 constructors, QtWidgets family coverage and reversible enhancements, composites, Gallery, Designer metadata, and real `.ui` reconstruction are covered |
| Python type information | Shipped | The wheel carries the PEP 561 `py.typed` marker and CI fails when it is missing |
| Designer host smoke test | Passing on macOS | `pyside6-designer` opened a custom-widget `.ui` offscreen with no registration/import errors |
| Python package | Published | Core 0.2.6 is on PyPI; wheel and sdist pass metadata/content checks, exclude private Pro implementation, and are verified through isolated PySide6 and PyQt installation tests |
| Component gallery | Available | Searchable light/dark application provides interactive previews for all 66 public Core components plus four pages made only from stock QtWidgets |
| C++ foundation | Available | Button, Input, Card, CMake install package, generated QSS resources; compiled with Qt 6.9 |
| Documentation | Passing | VitePress production build succeeds |
| Visual profile | Verified | Classic `new-york` geometry and interaction states with the Zinc light/dark palette, plus Chrome-style document tabs; all 66 Gallery previews render and the core metrics are covered by automated contract tests |
| Native screenshot regression | Available, platform-scoped | Four stock-QtWidgets Gallery pages have committed light/dark baselines (8 images) with tolerant perceptual regression tests and a reproducible update script; baselines live in a per-platform directory and a platform without baselines skips instead of failing |

## Continuous integration

`.github/workflows/ci.yml` runs six jobs:

| Job | Platform | Coverage |
|---|---|---|
| `lint` | ubuntu | `ruff check` over the package, the tools, and the example gallery |
| `artifacts` | ubuntu | Regenerates tokens and fails on any diff, so generated code cannot drift |
| `checks` | ubuntu, Python 3.9/3.11/3.13 | License, version, branding, and Core/Pro boundary checks plus the full suite **without** a Qt binding to prove the degraded import path |
| `qt` | ubuntu | Full suite on PySide6 and PyQt6 with `QT_QPA_PLATFORM=offscreen` |
| `windows` | windows-latest | Full suite on PySide6 with `QT_QPA_PLATFORM=offscreen` |
| `package` | ubuntu | Builds the wheel and sdist, validates their contents (including `py.typed`), and runs `twine check --strict` |

PyQt5 is deliberately outside the matrix. Qt 5.15 crashes with an access violation when the `offscreen` platform plugin shows a `QMessageBox`; a bare PyQt5 script with no shadcn-qt code reproduces it, so the failure is in the binding/platform pair, not in this project. PyQt5 therefore stays a manually verified desktop binding — see `docs/NATIVE_WIDGETS`-style desktop runs in `CONTRIBUTING.md` — until an offscreen-safe configuration is found.

The screenshot tests skip when the running platform has no font database, because baselines record rendered text.

## Verified matrix

Measured on Windows 11 with PySide6 6.8.3, PyQt6 6.8.1, and PyQt5 5.15.11, `QT_QPA_PLATFORM=offscreen`, and `QT_QPA_FONTDIR` pointed at the system font directory:

| Binding | Result |
|---|---|
| PySide6 | 76 passed, 8 skipped |
| PyQt6 | 76 passed, 8 skipped |
| PyQt5 | manual desktop runs only; offscreen crashes inside Qt (see above) |
| no binding | 16 passed, 68 skipped |

The eight skips are the Windows screenshot baselines, which have not been generated yet. Linux and macOS baselines remain macOS-rendered and are validated by the `qt` job.

## shadcn/ui alignment

The public Python catalog now provides a Qt-native class for every named component in the current shadcn/ui index. Its visual baseline is the classic `new-york` registry with the Zinc palette. Web-only implementation details are intentionally translated instead of copied: Radix DOM primitives become QWidget composition, CSS direction providers become a `Direction` container, Recharts becomes a dependency-free Qt-painted `Chart`, and typography CSS becomes a `Typography.level` property. The audited geometry and translation rules are recorded in `docs/STYLE_BASELINE.md`.

This is visual-contract and intent alignment, not a claim that different platform font rasterizers produce byte-identical browser pixels. The Qt classes retain native signals, models, focus handling, accessibility hooks, layouts, and Designer serialization while matching the new-york dimensions, semantic states, elevation hierarchy, and selection glyphs.

## Remaining hardening work

- Bring the C++ widget catalog to parity with the Python catalog; the three current widgets are the smallest part of the project.
- Add native Designer plugins for C++ consumers; the current drag/drop integration is Python-hosted and the recommended host is `pyside6-designer`.
- Generate Windows screenshot baselines on a real desktop session (the tests currently skip there) and add PySide2 coverage under an older supported Python.
- Add deeper keyboard/focus conformance tests and accessibility checks: no component currently overrides key handling or sets `setAccessibleName`, so keyboard-only operation, focus rings, and screen-reader labels are unverified for Accordion, Carousel, Command, InputOTP, and DataTable.
- Extend the basic `Chart` and `DataTable` mappings with optional high-volume/virtualized adapters without making the core package depend on QtCharts or third-party plotting libraries.
- Reconsider PyQt5 in CI once an offscreen-safe binding/platform combination is identified, and keep the manual desktop check documented meanwhile.
- Configure PyPI Trusted Publishing for future releases and publish signed CMake release artifacts.

These are tracked as further milestones rather than being hidden behind a claim of identical web and desktop behavior.
