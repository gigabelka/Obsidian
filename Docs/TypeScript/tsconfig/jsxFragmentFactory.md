# `jsxFragmentFactory`

Specify the JSX fragment factory function to use when targeting react JSX emit with [`jsxFactory`](jsxFactory.md) compiler option is specified, e.g. `Fragment`.

For example with this TSConfig:

```json
{
  "compilerOptions": {
    "target": "esnext",
    "module": "commonjs",
    "jsx": "react",
    "jsxFactory": "h",
    "jsxFragmentFactory": "Fragment"
  }
}
```

This TSX file:

```tsx
import { h, Fragment } from "preact";

const HelloWorld = () => (
  <>
    <div>Hello</div>
  </>
);
```

Would look like:

```tsx
import { h, Fragment } from "preact";

const HelloWorld = () => (
  <>
    <div>Hello</div>
  </>
);
```

This option can be used on a per-file basis too similar to [Babel's `/* @jsxFrag h */` directive](https://babeljs.io/docs/en/babel-plugin-transform-react-jsx#fragments).

For example:

```tsx
/** @jsx h */
/** @jsxFrag Fragment */

import { h, Fragment } from "preact";

const HelloWorld = () => (
  <>
    <div>Hello</div>
  </>
);
```
