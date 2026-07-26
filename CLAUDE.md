# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository. All answers must be in Russian.

## What this repository is

An Obsidian vault (synced via Yandex.Disk, versioned with git) that holds offline programming documentation libraries, not an application. There is no build, lint, or test setup. The content is plain Markdown with relative links, meant to be read/searched with any tool.

## Structure

- `Docs/` — the documentation vault content. [Docs/INDEX.md](Docs/INDEX.md) is the central index.
  - Each technology gets its own top-level folder (`Docs/React/`, `Docs/TypeScript/`, future techs follow the same pattern) with its own `INDEX.md` table of contents.
  - `Docs/React/` is a full offline snapshot of react.dev: `learn/` (guides), `reference/` (API), `errors/`, `warnings/`, `images/`.
  - `Docs/TypeScript/` is a full offline snapshot of typescriptlang.org: `handbook/`, `reference/`, `tsconfig/` (one page per compiler option), `tutorials/`, `release-notes/`, `modules-reference/`, `declaration-files/`, `javascript/`, `project-config/`, `get-started/`, `images/`.
- `_scripts/` — the tooling that generates and validates the docs (see below).

When asked React questions, find the right page via `Docs/React/INDEX.md` or grep `Docs/React/` directly, then answer from the local files rather than the web. Same for TypeScript: `Docs/TypeScript/INDEX.md`, or grep `Docs/TypeScript/tsconfig/` for compiler flags (file names are flag names).

## Commands

Run from the repository root:

- Regenerate the React docs: `python _scripts/convert_react_docs.py`
  - Converts the react.dev MDX source into vault Markdown. Source defaults to `c:\Temp\react.dev-main`; override with `REACT_SRC` / `REACT_DST` env vars.
  - This overwrites everything under `Docs/React/` and regenerates its `INDEX.md` — don't hand-edit files there, fix the converter instead.
- Regenerate the TypeScript docs: `python _scripts/convert_typescript_docs.py`
  - Converts the typescriptlang.org v2 source into vault Markdown. Source defaults to `c:\Temp\TypeScript-Website-2`; override with `TS_SRC` / `TS_DST` env vars.
  - This overwrites everything under `Docs/TypeScript/` and regenerates its `INDEX.md` — don't hand-edit files there, fix the converter instead.
- Validate links afterward: `python _scripts/check_links.py Docs/React` or `python _scripts/check_links.py Docs/TypeScript` (reports broken relative links and missing anchors; defaults to `Docs/React`).

## Content conventions (enforced by the converter)

These matter when editing converter output or adding new docs by hand:

- react.dev MDX components become Obsidian callouts: Note/Pitfall/DeepDive/Hint/Wip → `> [!note|warning|info|tip]`.
- Sandpacks become plain fenced code blocks, one per file, each preceded by a bold file name (`**src/App.js**`). TypeScript twoslash blocks are handled the same way: the `twoslash` flag, `// @directive` lines and `^?` markers are stripped, and `// @filename:` samples are split into per-file blocks with bold names.
- Internal links are relative `.md` links; links to site sections not in the vault stay absolute (`https://react.dev/...`, `https://www.typescriptlang.org/...`). TypeScript permalinks (`/docs/handbook/*.html`, `/tsconfig#flag`) are resolved to vault pages.
- Anchor links use Obsidian format (`#Heading text`, GitHub slugs are rewritten by the converter); parentheses in anchors are percent-encoded (`%28`/`%29`).
- Images are copied into `<Tech>/images/` and referenced with relative paths.
- TypeScript output file names are slugified to kebab-case (`Everyday Types.md` → `everyday-types.md`); tsconfig option pages keep their camelCase flag names.
