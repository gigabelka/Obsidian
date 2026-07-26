# `noLib`

Disables the automatic inclusion of any library files.
If this option is set, `lib` is ignored.

TypeScript _cannot_ compile anything without a set of interfaces for key primitives like: `Array`, `Boolean`, `Function`, `IArguments`, `Number`, `Object`, `RegExp`, and `String`. It is expected that if you use `noLib` you will be including your own type definitions for these.
