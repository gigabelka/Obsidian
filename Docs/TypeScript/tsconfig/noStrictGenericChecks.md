# `noStrictGenericChecks`

TypeScript will unify type parameters when comparing two generic functions.

```ts
type A = <T, U>(x: T, y: U) => [T, U];
type B = <S>(x: S, y: S) => [S, S];

function f(a: A, b: B) {
  b = a; // Ok
  a = b; // Error
}
```

This flag can be used to remove that check.
