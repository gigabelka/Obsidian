# resumeAndPrerenderToNodeStream

`resumeAndPrerenderToNodeStream` continues a prerendered React tree to a static HTML string using a a [Node.js Stream.](https://nodejs.org/api/stream.html).

```js
const {prelude, postponed} = await resumeAndPrerenderToNodeStream(reactNode, postponedState, options?)
```

> [!note]
>
> This API is specific to Node.js. Environments with [Web Streams,](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API) like Deno and modern edge runtimes, should use [`prerender`](prerender.md) instead.
>

---

## Reference

### `resumeAndPrerenderToNodeStream(reactNode, postponedState, options?)`

Call `resumeAndPrerenderToNodeStream` to continue a prerendered React tree to a static HTML string.

```js
import { resumeAndPrerenderToNodeStream } from 'react-dom/static';
import { getPostponedState } from 'storage';

async function handler(request, writable) {
  const postponedState = getPostponedState(request);
  const { prelude } = await resumeAndPrerenderToNodeStream(<App />, JSON.parse(postponedState));
  prelude.pipe(writable);
}
```

On the client, call [`hydrateRoot`](../client/hydrateRoot.md) to make the server-generated HTML interactive.

[See more examples below.](#Usage)

#### Parameters

* `reactNode`: The React node you called `prerender` (or a previous `resumeAndPrerenderToNodeStream`) with. For example, a JSX element like `<App />`. It is expected to represent the entire document, so the `App` component should render the `<html>` tag.
* `postponedState`: The opaque `postpone` object returned from a [prerender API](index.md), loaded from wherever you stored it (e.g. redis, a file, or S3).
* **optional** `options`: An object with streaming options.
  * **optional** `signal`: An [abort signal](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal) that lets you [abort server rendering](#aborting-server-rendering) and render the rest on the client.
  * **optional** `onError`: A callback that fires whenever there is a server error, whether [recoverable](#recovering-from-errors-outside-the-shell) or [not.](#recovering-from-errors-inside-the-shell) By default, this only calls `console.error`. If you override it to [log crash reports,](#logging-crashes-on-the-server) make sure that you still call `console.error`.

#### Returns

`resumeAndPrerenderToNodeStream` returns a Promise:
- If rendering the is successful, the Promise will resolve to an object containing:
  - `prelude`: a [Web Stream](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API) of HTML. You can use this stream to send a response in chunks, or you can read the entire stream into a string.
  - `postponed`: an JSON-serializeable, opaque object that can be passed to [`resumeToNodeStream`](../server/resume.md) or [`resumeAndPrerenderToNodeStream`](resumeAndPrerenderToNodeStream.md) if `resumeAndPrerenderToNodeStream` is aborted.
- If rendering fails, the Promise will be rejected. [Use this to output a fallback shell.](../server/renderToReadableStream.md#Recovering from errors inside the shell)

#### Caveats

`nonce` is not an available option when prerendering. Nonces must be unique per request and if you use nonces to secure your application with [CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP) it would be inappropriate and insecure to include the nonce value in the prerender itself.

> [!note]
>
> ### When should I use `resumeAndPrerenderToNodeStream`?
>
> The static `resumeAndPrerenderToNodeStream` API is used for static server-side generation (SSG). Unlike `renderToString`, `resumeAndPrerenderToNodeStream` waits for all data to load before resolving. This makes it suitable for generating static HTML for a full page, including data that needs to be fetched using Suspense. To stream content as it loads, use a streaming server-side render (SSR) API like [renderToReadableStream](../server/renderToReadableStream.md).
>
> `resumeAndPrerenderToNodeStream` can be aborted and later either continued with another `resumeAndPrerenderToNodeStream` or resumed with `resume` to support partial pre-rendering.
>

---

## Usage

### Further reading

`resumeAndPrerenderToNodeStream` behaves similarly to [`prerender`](prerender.md) but can be used to continue a previously started prerendering process that was aborted.
For more information about resuming a prerendered tree, see the [resume documentation](../server/resume.md#Resuming a prerender).
