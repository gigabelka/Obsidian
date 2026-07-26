# `suppressImplicitAnyIndexErrors`

Turning `suppressImplicitAnyIndexErrors` on suppresses reporting the error about implicit anys when indexing into objects, as shown in the following example:

```ts
const obj = { x: 10 };
console.log(obj["foo"]);
```

Using `suppressImplicitAnyIndexErrors` is quite a drastic approach. It is recommended to use a `@ts-ignore` comment instead:

```ts
const obj = { x: 10 };
// @ts-ignore
console.log(obj["foo"]);
```
