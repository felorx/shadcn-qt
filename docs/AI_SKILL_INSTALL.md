# Install the shadcn-qt AI Skill

The canonical, vendor-neutral skill source is:

```text
skills/developing-shadcn-qt/
```

Do not edit an installed copy under `.cursor`, `.agents`, or a user-level skill
directory. Edit the canonical source and reinstall or use a symbolic link.

## Instructions for AI Agents

When asked to install this skill:

1. Resolve the repository root and verify that
   `skills/developing-shadcn-qt/SKILL.md` exists.
2. Determine which skill discovery directory the active AI host supports.
3. Prefer a symbolic link so updates to the canonical skill take effect without
   copying files. Link the entire skill directory, not only `SKILL.md`, because
   the skill also contains references and metadata.
4. Use exactly `developing-shadcn-qt` as the installed directory name.
5. Verify that the installed path resolves to the canonical directory and that
   `SKILL.md` remains readable. Restart the host only if it does not detect the
   change automatically.
6. Do not commit host-specific installation links. They are local adapters and
   are ignored by this repository.

## Codex: Repository-Scoped Installation

From the repository root, create a link in Codex's repository skill directory:

```bash
mkdir -p .agents/skills
ln -sfn ../../skills/developing-shadcn-qt .agents/skills/developing-shadcn-qt
test -f .agents/skills/developing-shadcn-qt/SKILL.md
```

Codex scans `.agents/skills` from the current working directory up to the
repository root and supports linked skill directories. This is the preferred
installation for work limited to this repository.

For a user-scoped Codex installation, resolve this repository to an absolute
path and link the same complete directory as
`$HOME/.agents/skills/developing-shadcn-qt`.

## Cursor: Repository-Scoped Installation

From the repository root, expose the same canonical source to Cursor:

```bash
mkdir -p .cursor/skills
ln -sfn ../../skills/developing-shadcn-qt .cursor/skills/developing-shadcn-qt
test -f .cursor/skills/developing-shadcn-qt/SKILL.md
```

This compatibility link does not make `.cursor` the source of truth.

## Other AI Hosts

Consult the host's documentation for its local skill discovery directory, then
link or copy the complete `skills/developing-shadcn-qt` directory there. If the
host implements the Agent Skills standard, it should recognize the included
`SKILL.md`; relative references must remain inside the installed directory.

After installation, invoke the skill explicitly as `$developing-shadcn-qt` if
the host supports named invocation, or ask the host to use the
`developing-shadcn-qt` skill for repository changes.

For the current Codex skill format and discovery locations, see the official
[Build skills documentation](https://learn.chatgpt.com/codex/build-skills).
