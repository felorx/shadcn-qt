# Developing shadcn-qt Skill Design

## Purpose

Create a project-scoped Cursor Agent Skill that helps AI agents make correct
core-development changes in this repository. It targets Python widgets, design
tokens, QSS themes, Qt Designer integration, tests, and component
documentation. C++ is covered only as a parity boundary, not as a default
implementation target.

## Goals

- Make repository-specific source-of-truth rules discoverable before an agent
  edits a component or theme.
- Direct agents to the complete set of affected files for common change types.
- Preserve native Qt behavior, single-binding compatibility, generated artifacts,
  and the project's dual-license contribution constraints.
- Keep default prompt cost low by placing detailed paths and commands in a
  reference file.

## Non-goals

- Publishing packages, managing release credentials, or handling commercial
  order processes.
- Replacing existing contributor documentation or CI configuration.
- Treating the incomplete C++ catalog as equal in scope to the Python catalog.

## Skill Layout

```text
.cursor/skills/developing-shadcn-qt/
├── SKILL.md
└── reference.md
```

`SKILL.md` will omit `disable-model-invocation` so that an agent can discover
it automatically for relevant repository tasks. The skill and reference will
use English to match the repository's code and contributor documentation.

## Main Skill Contract

The skill will use the following discovery metadata:

```yaml
name: developing-shadcn-qt
description: Use when adding or changing shadcn-qt Python widgets, Qt Designer integration, semantic tokens, QSS themes, project tests, or component documentation in this repository.
```

The main file will remain concise and give agents a task-based workflow:

1. Identify whether the task changes a Python widget, tokens, theme behavior,
   Designer support, documentation, or a combination.
2. Inspect the closest existing implementation before editing.
3. Apply the matching repository contract:
   - Python widgets inherit the appropriate Qt class, preserve native signals,
     and use the shared component initialization helpers.
   - Enum-like widget state uses the project helper rather than recursively
     setting a declared Qt property.
   - Designer-facing properties use the existing camelCase and accessor
     patterns; size is exposed as `shadcnSize`.
   - Token changes start at `packages/design-tokens/tokens.json`, then run the
     generator. Generated Python, QSS, and C++ artifacts are never edited by
     hand.
   - Theme and native-widget changes preserve the documented `configure`,
     `apply_theme`, and `enable_native_widget_styling` boundaries.
4. Update the affected public API, Designer registry, tests, and component docs
   when the task requires them.
5. Run only the relevant quality gates, then expand validation to the CI
   equivalents when the change crosses source-of-truth boundaries.

The skill will also state that Python is the default implementation surface;
C++ work needs an explicit request or a concrete parity requirement.

## Reference File

`reference.md` will contain:

- The monorepo map and authoritative files for tokens, widgets, generated
  artifacts, Designer registration, tests, docs, and C++.
- The supported Qt binding rule: one binding per process, with
  `SHADCN_QT_BINDING` or the project detector used when selection matters.
- The default offscreen test environment and CI-aligned commands.
- The contributor requirements: no unreviewed third-party source copying and
  the exact CLA statement for non-trivial external contributions.
- Stable terminology: distribution name `shadcn-qt`, Python import
  `shadcn_qt`, and shadcn-aligned PascalCase component names.

## Validation Strategy

The skill will be tested as process documentation with fresh agent scenarios.
Before authoring the skill, run these baseline scenarios without it:

1. Add a Python widget under time pressure and check whether the agent finds
   public API, Designer, test, and documentation integration points.
2. Change a semantic token and check whether the agent edits the source JSON
   and regenerates all outputs instead of hand-editing generated files.
3. Add a Designer-facing property and check whether the agent preserves the
   existing Qt property/accessor conventions.

Classify the observed baseline results before authoring. If a scenario exposes
a gap, add only the minimal corrective guidance needed to close it. If the
baseline is already fully correct, no corrective guidance is needed; retain the
reference skill only when the documented rationale is that the user explicitly
requested a repository reference. In both cases, rerun the same scenarios with
the skill loaded to verify correct application and non-regression.

## Acceptance Criteria

- The skill is located under `.cursor/skills/` and consists only of the main
  skill and one direct reference file.
- Its metadata is valid, searchable, and has a third-person trigger-only
  description.
- `SKILL.md` is under 500 lines and directs agents to `reference.md` only when
  detailed repository facts are needed.
- With the skill loaded, the validation scenarios remain correct, name the
  applicable source-of-truth files and validation commands, and introduce no
  unsupported release or C++ scope.
- When no baseline gap exists, the validation record documents the user's
  explicit request for a repository reference instead of claiming behavioral
  improvement.
- No generated output, production package source, or unrelated project files
  are changed.
