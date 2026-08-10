# shadcn-qt Development Reference

## Source Map

| Change | Authoritative path | Related paths |
| --- | --- | --- |
| Semantic colors, radius, font | `packages/design-tokens/tokens.json` | `tools/token-codegen/generate.py`, `packages/python/shadcn_qt/_generated/`, `packages/python/shadcn_qt/_generated/base_light.qss`, `packages/python/shadcn_qt/_generated/base_dark.qss`, `packages/cpp/shadcn_qt/include/shadcn_qt/ThemeTokens.h` |
| Python widgets | `packages/python/shadcn_qt/widgets/` | `packages/python/shadcn_qt/widgets/_helpers.py`, `packages/python/shadcn_qt/widgets/__init__.py`, `packages/python/shadcn_qt/__init__.py`, `packages/python/shadcn_qt/_stylesheet.py` |
| Themes | `packages/python/shadcn_qt/theme.py` | `packages/python/shadcn_qt/_stylesheet.py`, `packages/python/tests/test_theme.py` |
| Native Qt adoption | `packages/python/shadcn_qt/native.py` | `packages/python/tests/test_native_widgets.py`, `apps/docs/guide/migration.md` |
| Qt Designer | `packages/python/shadcn_qt/designer/` | `packages/python/shadcn_qt/designer/registry.py`, `packages/python/tests/test_designer.py`, `examples/python_designer/` |
| Widget checks | `packages/python/tests/test_widgets.py` | `packages/python/tests/test_composite_widgets.py`, `packages/python/tests/test_import_core.py` |
| Component docs | `apps/docs/components/catalog.md` | `apps/docs/guide/designer.md`, `apps/docs/guide/migration.md` |

## Widget Rules

- Python distribution name: `shadcn-qt`; Python import: `shadcn_qt`.
- Use shadcn-aligned PascalCase public class names and a kebab-case component name for `initialize_component`.
- Retain the native Qt class's signals, slots, models, focus behavior, layouts, and accessibility behavior.
- Use `set_choice_property` for restricted values. It validates, refreshes QSS, and avoids recursive declared-property setters.
- Add a direct Designer `Spec` only when the automatic catalogue entry needs a custom tooltip, container flag, or initial XML.

## Token and Theme Rules

```bash
python tools/token-codegen/generate.py
python tools/check_licenses.py
python tools/check_versions.py
```

`tokens.json` is the source of truth. The generator writes Python theme data,
light/dark QSS, and the C++ token header. Do not edit its outputs by hand.

Use `configure` for process-wide defaults, `apply_theme` to set a theme on a
`QApplication`, and `enable_native_widget_styling` only for opt-in styling of
existing native widgets. Native adoption is intentionally reversible with
`disable_native_widget_styling`.

## Bindings and Tests

- Support PySide6, PyQt6, PySide2, and PyQt5 through one public API.
- A process may load only one binding. Use `SHADCN_QT_BINDING` or
  `detect_binding()` when binding selection matters.
- Keep Qt tests headless:

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=packages/python python -m pytest packages/python/tests -q
```

- CI regenerates artifacts, checks synchronized licenses and versions, then
  runs the Python test suite. Documentation validation is:

```bash
(cd apps/docs && npm ci && npm run build)
```

## Contribution Constraints

- The project is GPL-3.0-only or commercially licensed.
- Do not submit copied third-party source unless its provenance and license
  have been reviewed and recorded.
- Non-trivial external pull requests require this exact statement:

```text
I have read and agree to the shadcn-qt CLA v1.0: NAME, YYYY-MM-DD
```

- State that shadcn-qt is independent and not affiliated with shadcn, Vercel,
  The Qt Company, or Riverbank Computing when changing project-facing copy.
