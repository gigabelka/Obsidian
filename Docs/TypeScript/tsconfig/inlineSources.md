# `inlineSources`

When set, TypeScript will include the original content of the `.ts` file as an embedded string in the source map (using the source map's `sourcesContent` property).
This is often useful in the same cases as [`inlineSourceMap`](inlineSourceMap.md).

Requires either [`sourceMap`](sourceMap.md) or [`inlineSourceMap`](inlineSourceMap.md) to be set.

For example, with this TypeScript:

```ts
const helloWorld = "hi";
console.log(helloWorld);
```

By default converts to this JavaScript:

```ts
const helloWorld = "hi";
console.log(helloWorld);
```

Then enable building it with `inlineSources` and [`inlineSourceMap`](inlineSourceMap.md) enabled there is a comment at the bottom of the file which includes
a source-map for the file.
Note that the end is different from the example in [`inlineSourceMap`](inlineSourceMap.md) because the source-map now contains the original source code also.

```ts
const helloWorld = "hi";
console.log(helloWorld);
```
