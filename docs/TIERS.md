# Community vs Pro

This repository documents how **qtshadcn** splits scope between the open-source **Community** edition and a future **Pro** (commercial) offering.

## Community (free / OSS)

- **License**: MIT (see repository root `LICENSE`).
- **Components**: Core primitives aligned with [shadcn/ui](https://ui.shadcn.com/) — Button (variants), Input, Card, Separator, and future basics (Checkbox, Radio, Switch, Tabs, Dialog skeleton, etc.).
- **Theming**: Light/dark from shared design tokens; `tools/token-codegen` generates QSS + Python + C++ artifacts.
- **Bindings**: Python (`PySide6`, `PyQt6`, `PySide2`, `PyQt5`) and C++ (Qt 5.15+ and Qt 6.x).
- **Tooling**: Token/codegen CLI, public documentation site source under `apps/docs`.

## Pro (planned commercial)

- **License**: Commercial license (sold separately); not included in the default OSS build.
- **Components**: Heavy widgets — virtualized DataTable, advanced navigation shells, charts, rich text toolbars, Qt Designer plugins, full page templates.
- **Theming**: Multi-brand packs, design-tool sync, contrast/accessibility preset bundles.
- **Tooling**: Private component registry, team theme sync, visual regression CI integrations, SLA support.

## Code layout

- Community code lives under `packages/python/qtshadcn` and `packages/cpp/qtshadcn`.
- The `packages/python/qtshadcn/pro` package is reserved; importing it in OSS builds raises a clear error directing users to Pro distribution (see `pro/__init__.py`).
