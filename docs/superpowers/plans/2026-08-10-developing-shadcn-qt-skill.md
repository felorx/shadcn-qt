# Developing shadcn-qt Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an automatically discoverable, project-scoped Cursor Agent Skill that guides correct core-development work in shadcn-qt.

**Architecture:** The deliverable has a concise `SKILL.md` for decisions and non-negotiable project rules, plus a direct `reference.md` for paths and commands. Fresh-agent baseline and loaded-skill scenarios validate correctness and non-regression. If the baseline is already fully correct, the documented user request for a repository reference—not a claimed behavioral improvement—justifies retaining the skill without changing package source, generated artifacts, or release workflows.

**Tech Stack:** Cursor Agent Skills (Markdown/YAML), Qt/Python repository conventions, local fresh-agent scenarios, Python static validation.

## Global Constraints

- Create the skill under `.cursor/skills/developing-shadcn-qt/` so it is shared with repository users.
- Use the exact skill name `developing-shadcn-qt`.
- The frontmatter description starts with `Use when...`, is third-person, and describes only trigger conditions.
- Omit `disable-model-invocation` so relevant agents can discover the project skill automatically.
- Write the skill and reference in English, matching repository code and contributor documentation.
- Treat Python widgets as the default implementation surface; C++ needs an explicit request or a concrete parity requirement.
- Never direct agents to hand-edit `packages/python/shadcn_qt/_generated/` or `packages/cpp/shadcn_qt/include/shadcn_qt/ThemeTokens.h`.
- Do not commit or push any change unless the user explicitly requests it.
- No package source, generated artifact, token, documentation-site, or CI changes are part of this work.

---

## File Structure

```text
.cursor/skills/developing-shadcn-qt/
├── SKILL.md       # Auto-discoverable workflow and invariants
└── reference.md   # Paths, commands, compatibility, and contribution details
```

| File | Responsibility |
| --- | --- |
| `.cursor/skills/developing-shadcn-qt/SKILL.md` | Defines when the skill applies and the concise task-based workflows an agent must follow. |
| `.cursor/skills/developing-shadcn-qt/reference.md` | Holds the monorepo map, source-of-truth chain, validation commands, Qt binding rules, and contribution constraints. |
| `docs/superpowers/plans/2026-08-10-developing-shadcn-qt-skill.md` | Records this executable implementation and validation plan. |

### Task 1: Establish the No-Skill Baseline

**Files:**
- Create: none
- Modify: none
- Test: three fresh, read-only agent scenarios recorded in the task transcript

**Interfaces:**
- Consumes: the repository at `/path/to/shadcn-qt` without a project skill.
- Produces: verbatim baseline answers for scenarios `P1`, `P2`, and `P3`, plus a list of repository-specific gaps.

- [ ] **Step 1: Run the new-widget pressure scenario without a skill**

Use a fresh agent with this exact prompt. The agent may inspect files but must not edit them:

```text
You are working in /path/to/shadcn-qt. Under time pressure, propose the exact repository changes needed to add a public Python `Tag` widget: a lightweight QLabel-derived status component with `default`, `secondary`, `outline`, and `destructive` variants that works in Qt Designer. Do not edit files. List every file to change and every validation command you would run.
```

Record the answer verbatim under `P1`. Mark these omissions if they occur: the public widget catalogue, lazy root API catalogue, shared helper/property conventions, QSS renderer, Designer registry behavior, widget tests, or component documentation.

- [ ] **Step 2: Run the token source-of-truth pressure scenario without a skill**

Use a different fresh agent with this exact prompt:

```text
You are working in /path/to/shadcn-qt. A maintainer asks for the default `primary` token to change in both built-in themes and wants Python, QSS, and C++ distributions to remain synchronized. Do not edit files. Give the exact source file, generated outputs that must not be edited manually, commands to run, and checks to run before a pull request.
```

Record the answer verbatim under `P2`. Mark whether it identifies
`packages/design-tokens/tokens.json`, `tools/token-codegen/generate.py`, all
generated artifacts, `tools/check_licenses.py`, and `tools/check_versions.py`.

- [ ] **Step 3: Run the Designer property pressure scenario without a skill**

Use a third fresh agent with this exact prompt:

```text
You are working in /path/to/shadcn-qt. Add a Qt Designer-editable string property named `tone` to Button, restricted to a finite allowed set. It must refresh QSS correctly and must not recurse when Designer calls Qt's property system. Do not edit files. Identify the existing implementation pattern, the forbidden setter pattern, and the focused tests to run.
```

Record the answer verbatim under `P3`. Mark whether it finds
`set_choice_property`, `qt_property`, camelCase getter/setter aliases, and the
warning against calling `QObject.setProperty` inside a declared Qt property's
setter.

- [ ] **Step 4: Classify baseline results**

Create a concise transcript table with columns `Scenario`, `Correct facts`,
`Missing or incorrect facts`, and `Skill guidance required`. A scenario proves
the baseline inadequate if it omits a source-of-truth rule or recommends an
unsafe operation. If all three outputs already meet every required criterion,
record that no corrective guidance is needed. Because the user has explicitly
requested a project reference, continue with a reference skill and document
that request as the retention rationale; do not claim behavioral improvement
over the passing baseline.

### Task 2: Author the Project Skill From the Baseline Gaps

**Files:**
- Create: `.cursor/skills/developing-shadcn-qt/SKILL.md`
- Create: `.cursor/skills/developing-shadcn-qt/reference.md`
- Modify: none
- Test: frontmatter, line-count, and reference-link validation in Task 4

**Interfaces:**
- Consumes: the classified `P1`/`P2`/`P3` baseline gaps from Task 1.
- Produces: `developing-shadcn-qt` as an auto-discoverable project skill with
  a direct `reference.md` dependency.

- [ ] **Step 1: Translate only observed gaps into concise instructions**

Use these repository facts as the fixed implementation contract:

- `packages/python/shadcn_qt/widgets/_helpers.py` owns
  `initialize_component`, `set_choice_property`, and style refresh behavior.
- Widget exports require the relevant import and `__all__` entry in
  `packages/python/shadcn_qt/widgets/__init__.py`, plus a matching name in
  `_WIDGET_NAMES` in `packages/python/shadcn_qt/__init__.py`.
- `packages/python/shadcn_qt/designer/registry.py` automatically derives most
  Designer `Spec` entries from `widget_module.__all__`; add an explicit `Spec`
  only for non-default tooltip, container, or initial XML behavior.
- `packages/python/shadcn_qt/_stylesheet.py` is the QSS renderer; generated
  QSS follows from token generation and is not hand-maintained.
- `packages/design-tokens/tokens.json` is the only semantic token source.

- [ ] **Step 2: Create `SKILL.md` with this exact content**

```markdown
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
- **Public widget:** update `shadcn_qt.widgets` exports and the root lazy `_WIDGET_NAMES` set. Add QSS selectors in `_stylesheet.py` when the component needs distinct styling. The Designer registry derives ordinary entries from `widgets.__all__`; add a `Spec` only for custom tooltip, container, or default XML behavior.
- **Token:** edit only `packages/design-tokens/tokens.json`, then run `python tools/token-codegen/generate.py`. Never hand-edit `_generated/`, generated QSS, or `ThemeTokens.h`.
- **Theme or native compatibility:** preserve the boundaries between `configure`, `apply_theme`, and `enable_native_widget_styling`; retain opt-in and reversible native-widget adoption.

## Validate

Run focused tests first, then the relevant commands in [reference.md](reference.md). Use one Qt binding per process and keep tests headless with `QT_QPA_PLATFORM=offscreen` when a binding is installed.

## Contribution Boundaries

Do not copy third-party source without reviewed provenance. For non-trivial external contributions, follow the exact CLA statement in `CONTRIBUTING.md`.
```

- [ ] **Step 3: Create `reference.md` with this exact content**

```markdown
# shadcn-qt Development Reference

## Source Map

| Change | Authoritative path | Related paths |
| --- | --- | --- |
| Semantic colors, radius, font | `packages/design-tokens/tokens.json` | `tools/token-codegen/generate.py`, Python `_generated/`, generated QSS, `packages/cpp/shadcn_qt/include/shadcn_qt/ThemeTokens.h` |
| Python widgets | `packages/python/shadcn_qt/widgets/` | `widgets/_helpers.py`, `widgets/__init__.py`, root `shadcn_qt/__init__.py`, `_stylesheet.py` |
| Themes | `packages/python/shadcn_qt/theme.py` | `_stylesheet.py`, `tests/test_theme.py` |
| Native Qt adoption | `packages/python/shadcn_qt/native.py` | `tests/test_native_widgets.py`, migration guide |
| Qt Designer | `packages/python/shadcn_qt/designer/` | `designer/registry.py`, `tests/test_designer.py`, `examples/python_designer/` |
| Widget checks | `packages/python/tests/test_widgets.py` | `tests/test_composite_widgets.py`, `tests/test_import_core.py` |
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
```

- [ ] **Step 4: Inspect the authored files before behavioral validation**

Run:

```bash
python - <<'PY'
from pathlib import Path

skill_dir = Path(".cursor/skills/developing-shadcn-qt")
skill = skill_dir / "SKILL.md"
reference = skill_dir / "reference.md"

assert skill.is_file(), skill
assert reference.is_file(), reference
content = skill.read_text(encoding="utf-8")
assert content.startswith("---\nname: developing-shadcn-qt\n")
assert "description: Use when " in content
assert "disable-model-invocation" not in content
assert "[reference.md](reference.md)" in content
assert len(content.splitlines()) < 500
print("skill structure valid")
PY
```

Expected: `skill structure valid`.

### Task 3: Run Fresh-Agent Scenarios With the Skill and Refine It

**Files:**
- Modify: `.cursor/skills/developing-shadcn-qt/SKILL.md` only if a scenario exposes a missing decision rule
- Modify: `.cursor/skills/developing-shadcn-qt/reference.md` only if a scenario exposes a missing repository fact or command
- Test: the same `P1`, `P2`, and `P3` scenarios from Task 1

**Interfaces:**
- Consumes: the published `developing-shadcn-qt` skill and the exact prompts
  from Task 1.
- Produces: three answers that satisfy all scenario-specific acceptance checks.

- [ ] **Step 1: Run P1 with the skill loaded**

Use a fresh agent. Prepend this instruction to the P1 prompt:

```text
Before answering, read .cursor/skills/developing-shadcn-qt/SKILL.md and any directly linked reference it requires. Apply it to the task, but do not edit files.
```

Pass criteria: the plan identifies a native Qt superclass, `initialize_component`,
finite-choice property handling, `widgets/__init__.py`, root `_WIDGET_NAMES`,
QSS only when distinct styling is necessary, automatic Designer registration
with the explicit-`Spec` exception, focused widget/Designer tests, and component
documentation.

- [ ] **Step 2: Run P2 with the skill loaded**

Use a different fresh agent with the same read-first instruction and the exact
P2 prompt from Task 1.

Pass criteria: the answer names `packages/design-tokens/tokens.json` as the
only source, runs `python tools/token-codegen/generate.py`, explicitly avoids
hand-editing `_generated/`, generated QSS, and `ThemeTokens.h`, and includes
both version and license synchronization checks.

- [ ] **Step 3: Run P3 with the skill loaded**

Use a third fresh agent with the same read-first instruction and the exact P3
prompt from Task 1.

Pass criteria: the answer uses `set_choice_property`, a private backing
attribute, `qt_property`, camelCase aliases, `refresh_style` through the helper,
and explicitly rejects calling `QObject.setProperty` from the declared
property's setter.

- [ ] **Step 4: Refine minimally if a pass criterion is missed**

For each missed criterion, add one concise instruction at the decision point
where the agent made the error. Keep implementation patterns in `SKILL.md` and
move static paths or commands to `reference.md`. Re-run only the failed
scenario after each edit. Do not add speculative guidance for scenarios that
already pass.

### Task 4: Verify the Final Skill Artifact

**Files:**
- Verify: `.cursor/skills/developing-shadcn-qt/SKILL.md`
- Verify: `.cursor/skills/developing-shadcn-qt/reference.md`
- Verify: repository diff contains only the design document, plan, and two
  intended skill files

**Interfaces:**
- Consumes: the refined skill and passing agent scenarios.
- Produces: a valid, concise, discoverable project skill ready for review.

- [ ] **Step 1: Validate metadata, size, and direct references**

Run:

```bash
python - <<'PY'
from pathlib import Path

skill_dir = Path(".cursor/skills/developing-shadcn-qt")
skill = skill_dir / "SKILL.md"
reference = skill_dir / "reference.md"
content = skill.read_text(encoding="utf-8")

assert skill.is_file() and reference.is_file()
assert len(content.splitlines()) < 500
assert "name: developing-shadcn-qt" in content
assert content.count("[reference.md](reference.md)") == 1
assert "disable-model-invocation" not in content
assert reference.read_text(encoding="utf-8").startswith("# shadcn-qt Development Reference")
print("skill metadata and references valid")
PY
```

Expected: `skill metadata and references valid`.

- [ ] **Step 2: Scan for unfinished language and whitespace errors**

Run:

```bash
rg -n '\b(TODO|TBD|FIXME|XXX)\b' .cursor/skills/developing-shadcn-qt
git diff --check
```

Expected: `rg` returns no matches and `git diff --check` produces no output.

- [ ] **Step 3: Confirm the final diff stays in scope**

Run:

```bash
git status --short
git diff -- .cursor/skills/developing-shadcn-qt docs/superpowers
```

Expected: only the two skill files and the two process documents appear; no
package source, generated artifacts, tokens, documentation site, or CI file is
modified.

- [ ] **Step 4: Report results without creating a commit**

Report the skill path, the scenarios that passed, any minimal refinements made,
and the validation commands executed. Leave the working tree uncommitted unless
the user explicitly requests a Conventional Commit.
