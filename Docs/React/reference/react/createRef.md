# createRef

> [!warning] Pitfall
>
> `createRef` is mostly used for [class components.](Component.md) Function components typically rely on [`useRef`](useRef.md) instead.
>

`createRef` creates a [ref](../../learn/referencing-values-with-refs.md) object which can contain arbitrary value.

```js
class MyInput extends Component {
  inputRef = createRef();
  // ...
}
```

---

## Reference

### `createRef()`

Call `createRef` to declare a [ref](../../learn/referencing-values-with-refs.md) inside a [class component.](Component.md)

```js
import { createRef, Component } from 'react';

class MyComponent extends Component {
  intervalRef = createRef();
  inputRef = createRef();
  // ...
```

[See more examples below.](#Usage)

#### Parameters

`createRef` takes no parameters.

#### Returns

`createRef` returns an object with a single property:

* `current`: Initially, it's set to the `null`. You can later set it to something else. If you pass the ref object to React as a `ref` attribute to a JSX node, React will set its `current` property.

#### Caveats

* `createRef` always returns a *different* object. It's equivalent to writing `{ current: null }` yourself.
* In a function component, you probably want [`useRef`](useRef.md) instead which always returns the same object.
* `const ref = useRef()` is equivalent to `const [ref, _] = useState(() => createRef(null))`.

---

## Usage

### Declaring a ref in a class component

To declare a ref inside a [class component,](Component.md) call `createRef` and assign its result to a class field:

```js
import { Component, createRef } from 'react';

class Form extends Component {
  inputRef = createRef();

  // ...
}
```

If you now pass `ref={this.inputRef}` to an `<input>` in your JSX, React will populate `this.inputRef.current` with the input DOM node. For example, here is how you make a button that focuses the input:

```js
import { Component, createRef } from 'react';

export default class Form extends Component {
  inputRef = createRef();

  handleClick = () => {
    this.inputRef.current.focus();
  }

  render() {
    return (
      <>
        <input ref={this.inputRef} />
        <button onClick={this.handleClick}>
          Focus the input
        </button>
      </>
    );
  }
}
```

> [!warning] Pitfall
>
> `createRef` is mostly used for [class components.](Component.md) Function components typically rely on [`useRef`](useRef.md) instead.
>

---

## Alternatives

### Migrating from a class with `createRef` to a function with `useRef`

We recommend using function components instead of [class components](Component.md) in new code. If you have some existing class components using `createRef`, here is how you can convert them. This is the original code:

```js
import { Component, createRef } from 'react';

export default class Form extends Component {
  inputRef = createRef();

  handleClick = () => {
    this.inputRef.current.focus();
  }

  render() {
    return (
      <>
        <input ref={this.inputRef} />
        <button onClick={this.handleClick}>
          Focus the input
        </button>
      </>
    );
  }
}
```

When you [convert this component from a class to a function,](Component.md#Alternatives) replace calls to `createRef` with calls to [`useRef`:](useRef.md)

```js
import { useRef } from 'react';

export default function Form() {
  const inputRef = useRef(null);

  function handleClick() {
    inputRef.current.focus();
  }

  return (
    <>
      <input ref={inputRef} />
      <button onClick={handleClick}>
        Focus the input
      </button>
    </>
  );
}
```
