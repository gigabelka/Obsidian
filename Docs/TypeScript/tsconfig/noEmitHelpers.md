# `noEmitHelpers`

Instead of importing helpers with [`importHelpers`](importHelpers.md), you can provide implementations in the global scope for the helpers you use and completely turn off emitting of helper functions.

For example, using this `async` function in ES5 requires a `await`-like function and `generator`-like function to run:

```ts
const getAPI = async (url: string) => {
  // Get API
  return {};
};
```

Which creates quite a lot of JavaScript:

```ts
const getAPI = async (url: string) => {
  // Get API
  return {};
};
```

Which can be switched out with your own globals via this flag:

```ts
const getAPI = async (url: string) => {
  // Get API
  return {};
};
```
