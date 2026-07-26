# `noUnusedLocals`

Report errors on unused local variables.

```ts
const createKeyboard = (modelID: number) => {
  const defaultModelID = 23;
  return { type: "keyboard", modelID };
};
```
