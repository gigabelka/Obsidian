# `allowJs`

Allow JavaScript files to be imported inside your project, instead of just `.ts` and `.tsx` files. For example, this JS file:

**card.js**

```js
export const defaultCardDeck = "Heart";
```

When imported into a TypeScript file will raise an error:

**card.js**

```ts
module.exports.defaultCardDeck = "Heart";
// ---cut---
```

**index.ts**

```ts
import { defaultCardDeck } from "./card";

console.log(defaultCardDeck);
```

Imports fine with `allowJs` enabled:

**card.js**

```ts
module.exports.defaultCardDeck = "Heart";
// ---cut---
```

**index.ts**

```ts
import { defaultCardDeck } from "./card";

console.log(defaultCardDeck);
```

This flag can be used as a way to incrementally add TypeScript files into JS projects by allowing the `.ts` and `.tsx` files to live along-side existing JavaScript files.

It can also be used along-side [`declaration`](declaration.md) and [`emitDeclarationOnly`](emitDeclarationOnly.md) to [create declarations for JS files](../javascript/creating-dts-files-from-js.md).
