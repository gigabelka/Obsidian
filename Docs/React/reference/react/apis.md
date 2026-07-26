# Built-in React APIs

In addition to [Hooks](hooks.md) and [Components](components.md), the `react` package exports a few other APIs that are useful for defining components. This page lists all the remaining modern React APIs.

---

* [`createContext`](createContext.md) lets you define and provide context to the child components. Used with [`useContext`.](useContext.md)
* [`lazy`](lazy.md) lets you defer loading a component's code until it's rendered for the first time.
* [`memo`](memo.md) lets your component skip re-renders with same props. Used with [`useMemo`](useMemo.md) and [`useCallback`.](useCallback.md)
* [`startTransition`](startTransition.md) lets you mark a state update as non-urgent. Similar to [`useTransition`.](useTransition.md)
* [`act`](act.md) lets you wrap renders and interactions in tests to ensure updates have processed before making assertions.

---

## Resource APIs

*Resources* can be accessed by a component without having them as part of their state. For example, a component can read a message from a Promise or read styling information from a context.

To read a value from a resource, use this API:

* [`use`](use.md) lets you read the value of a resource like a [Promise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise) or [context](../../learn/passing-data-deeply-with-context.md).
```js
function MessageComponent({ messagePromise }) {
  const message = use(messagePromise);
  const theme = use(ThemeContext);
  // ...
}
```
