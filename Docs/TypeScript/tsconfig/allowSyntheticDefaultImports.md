# `allowSyntheticDefaultImports`

When set to true, `allowSyntheticDefaultImports` allows you to write an import like:

```ts
import React from "react";
```

instead of:

```ts
import * as React from "react";
```

When the module **does not** explicitly specify a default export.

For example, without `allowSyntheticDefaultImports` as true:

**utilFunctions.js**

```ts
const getStringLength = (str) => str.length;

module.exports = {
  getStringLength,
};
```

**index.ts**

```ts
import utils from "./utilFunctions";

const count = utils.getStringLength("Check JS");
```

This code raises an error because there isn't a `default` object which you can import. Even though it feels like it should.
For convenience, transpilers like Babel will automatically create a default if one isn't created. Making the module look a bit more like:

**utilFunctions.js**

```js
const getStringLength = (str) => str.length;
const allFunctions = {
  getStringLength,
};

module.exports = allFunctions;
module.exports.default = allFunctions;
```

This flag does not affect the JavaScript emitted by TypeScript, it's only for the type checking.
This option brings the behavior of TypeScript in-line with Babel, where extra code is emitted to make using a default export of a module more ergonomic.
