# `composite`

The `composite` option enforces certain constraints which make it possible for build tools (including TypeScript
itself, under `--build` mode) to quickly determine if a project has been built yet.

When this setting is on:

- The [`rootDir`](rootDir.md) setting, if not explicitly set, defaults to the directory containing the `tsconfig.json` file.

- All implementation files must be matched by an [`include`](include.md) pattern or listed in the [`files`](files.md) array. If this constraint is violated, `tsc` will inform you which files weren't specified.

- [`declaration`](declaration.md) defaults to `true`

You can find documentation on TypeScript projects in [the handbook](../project-config/project-references.md).
