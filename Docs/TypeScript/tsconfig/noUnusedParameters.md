# `noUnusedParameters`

Report errors on unused parameters in functions.

```ts
const createDefaultKeyboard = (modelID: number) => {
  const defaultModelID = 23;
  return { type: "keyboard", modelID: defaultModelID };
};
```

Parameters declaration with names starting with an underscore (`_`) are exempt from the unused parameter checking. e.g.:

```ts
const createDefaultKeyboard = (_modelID: number) => {
  return { type: "keyboard" };
};
```
