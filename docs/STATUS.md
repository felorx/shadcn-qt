# Project status

Last verified: 2026-08-07.

## Implemented and tested

| Area | Status | Evidence |
|---|---|---|
| Python binding selection | Complete foundation | Lazy single-binding loader for PySide6, PyQt6, PySide2, and PyQt5; strict environment override |
| Python component primitives | 15 available | Button, Input, TextArea, Card, Label, Checkbox, RadioButton, Switch, Select, Slider, Progress, Tabs, Badge, Alert, Separator |
| Designer Property Editor | Available | Custom Qt properties for variants, sizes, validation state, card elevation, and separator orientation |
| Designer Widget Box | Available | Registration catalog, container metadata, DOM XML, and `qtshadcn-designer` launcher |
| `.ui` runtime loading | Available | Unified `load_ui()` path for PyQt `uic` and PySide `QUiLoader` |
| Global themes | Available | Light/dark, semantic token overrides, radius/font overrides, custom QSS, reusable Theme objects, JSON loader |
| Token generation | Available | One renderer generates packaged Python and embedded C++ QSS |
| Python automated tests | Passing | 8/8 under PySide6 6.11, PyQt6 6.11, and PyQt5 5.15: import, themes, widgets, Designer metadata, and real `.ui` reconstruction |
| Designer host smoke test | Passing on macOS | `pyside6-designer` opened a custom-widget `.ui` offscreen with no registration/import errors |
| Python wheel | Passing | Built wheel, inspected packaged plugin/QSS contents, and loaded a Designer form from a clean target install |
| C++ foundation | Available | Button, Input, Card, CMake install package, generated QSS resources; compiled with Qt 6.9 |
| Documentation | Passing | VitePress production build succeeds |

## Remaining parity work

The foundation is usable, but it is not yet full one-for-one parity with the entire shadcn/ui web catalog.

- Add compound/interactive primitives: Dialog, Sheet, Popover, DropdownMenu, ContextMenu, Tooltip, Toast/Sonner, Accordion, Collapsible, Calendar, DatePicker, Command, Breadcrumb, Pagination, Table, and Skeleton.
- Bring the C++ widget catalog to parity with the Python catalog.
- Add native Designer plugins for C++ consumers; the current drag/drop integration is Python-hosted and the recommended host is `pyside6-designer`.
- Run live Widget Box visibility checks on Windows and Linux and add PySide2 coverage under an older supported Python. PySide6/PyQt6/PyQt5 are covered in the current macOS verification environment.
- Add visual regression snapshots, keyboard/focus conformance tests, accessibility checks, icons, and right-to-left layout coverage.
- Add CI matrices and publish signed PyPI/CMake release artifacts.

These are tracked as further milestones rather than being hidden behind a claim of full shadcn parity.
