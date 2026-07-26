# `keyofStringsOnly`

This flag changes the `keyof` type operator to return `string` instead of `string | number` when applied to a type with a string index signature.

This flag is used to help people keep this behavior from [before TypeScript 2.9's release](../release-notes/typescript-2.9.md#Support `number` and `symbol` named properties with `keyof` and mapped types).
