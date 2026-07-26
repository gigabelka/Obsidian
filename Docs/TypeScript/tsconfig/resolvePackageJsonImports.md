# `resolvePackageJsonImports`

`--resolvePackageJsonImports` forces TypeScript to consult [the `imports` field of `package.json` files](https://nodejs.org/api/packages.html#imports) when performing a lookup that starts with `#` from a file whose ancestor directory contains a `package.json`.

This option defaults to `true` under the `node16`, `nodenext`, and `bundler` options for [`--moduleResolution`](moduleResolution.md).
