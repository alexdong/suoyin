# AGENTS.md

## Purpose

This repository publishes `suoyin`, a CLI that generates compact Python symbol
manifests for codebases.

## Reuse First

Before adding any new module, class, function, or helper, inspect the existing
symbols with:

```bash
uvx suoyin
```

If you are working in a specific area, inspect that subtree first:

```bash
uvx suoyin src
uvx suoyin tools
```

Prefer extending or refactoring existing code over creating parallel helpers or
near-duplicate modules.

## Required Workflow

1. Run `uvx suoyin` before creating new top-level symbols.
2. Inspect the most relevant existing files before deciding where code belongs.
3. Reuse or consolidate existing implementations whenever possible.
4. If you add something new, explain why the existing code was not the right
   place.

In your final response, include a short `Reuse audit` that says:

- which existing symbols or files you checked
- what you reused or modified
- if you added something new, why duplication was avoided

## README Is Generated

The `Usage` block in `README.md` is generated from the current repository by:

```bash
uv run python tools/update_readme.py
```

If you change CLI behavior, manifest output, symbol formatting, or anything that
affects the README example, regenerate it and verify it is current with:

```bash
uv run python tools/update_readme.py --check
```

Do not hand-edit the generated block between:

- `<!-- README:USAGE:START -->`
- `<!-- README:USAGE:END -->`

## Versioning And Publishing

Package versions are derived from git history.

- Do not hard-code or manually bump `__version__`.
- The `0.1.0` tag is the baseline anchor tag.
- New release tags should use the form `vX.Y.Z`.
- Commits after the latest release tag produce `dev` versions automatically.

Before publishing, verify:

```bash
uv run suoyin --version
uv build
uvx twine check dist/*
```

The GitHub Actions publishing workflow lives at:

- `.github/workflows/publish.yml`

It publishes on `v*` tags and checks that the generated README usage block is
up to date.

## Editing Guidance

- Keep the CLI output compact and stable.
- Prefer ASCII in source files unless there is a real reason not to.
- Keep functions short and focused.
- Treat duplicated or highly similar code as a design bug.
