# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. All answers must be in Russian.

## What this repository is

An Obsidian vault (synced via Yandex.Disk, versioned with git) that holds offline programming documentation libraries, not an application. There is no build, lint, or test setup. The content is plain Markdown with relative links, meant to be read/searched with any tool.

## Structure

- `Docs/` — the documentation vault content. [Docs/INDEX.md](Docs/INDEX.md) is the central index.
  - Each technology gets its own top-level folder (`Docs/React/`, future techs follow the same pattern) with its own `INDEX.md` table of contents.
  - `Docs/React/` is a full offline snapshot of react.dev: `learn/` (guides), `reference/` (API), `errors/`, `warnings/`, `images/`.
  - `Docs/_scripts/` — the tooling that generates and validates the docs (see below).

When asked React questions, find the right page via `Docs/React/INDEX.md` or grep `Docs/React/` directly, then answer from the local files rather than the web.

## Commands

Run from `Docs/`:

- Regenerate the React docs: `python _scripts/convert_react_docs.py`
  - Converts the react.dev MDX source into vault Markdown. Source defaults to `c:\Temp\react.dev-main`; override with `REACT_SRC` / `REACT_DST` env vars.
  - This overwrites everything under `Docs/React/` and regenerates its `INDEX.md` — don't hand-edit files there, fix the converter instead.
- Validate links afterward: `python _scripts/check_links.py` (reports broken relative links and missing anchors; also useful standalone after edits).

## Content conventions (enforced by the converter)

These matter when editing converter output or adding new docs by hand:

- react.dev MDX components become Obsidian callouts: Note/Pitfall/DeepDive/Hint/Wip → `> [!note|warning|info|tip]`.
- Sandpacks become plain fenced code blocks, one per file, each preceded by a bold file name (`**src/App.js**`).
- Internal links are relative `.md` links; links to react.dev sections not in the vault stay absolute `https://react.dev/...` URLs.
- Anchor links use Obsidian format (`#Heading text`, GitHub slugs are rewritten by the converter); parentheses in anchors are percent-encoded (`%28`/`%29`).
- Images are copied into `<Tech>/images/` and referenced with relative paths.
