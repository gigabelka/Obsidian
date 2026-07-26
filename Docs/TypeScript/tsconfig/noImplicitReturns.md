# `noImplicitReturns`

When enabled, TypeScript will check all code paths in a function to ensure they return a value.

```ts
function lookupHeadphonesManufacturer(color: "blue" | "black"): string {
  if (color === "blue") {
    return "beats";
  } else {
    "bose";
  }
}
```
