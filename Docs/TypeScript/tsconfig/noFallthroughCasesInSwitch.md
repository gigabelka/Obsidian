# `noFallthroughCasesInSwitch`

Report errors for fallthrough cases in switch statements.
Ensures that any non-empty case inside a switch statement includes either `break`, `return`, or `throw`.
This means you won't accidentally ship a case fallthrough bug.

```ts
const a: number = 6;

switch (a) {
  case 0:
    console.log("even");
  case 1:
    console.log("odd");
    break;
}
```
