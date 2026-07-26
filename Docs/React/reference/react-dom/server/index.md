# Server React DOM APIs

The `react-dom/server` APIs let you server-side render React components to HTML. These APIs are only used on the server at the top level of your app to generate the initial HTML. A [framework](../../../learn/creating-a-react-app.md#Full-stack frameworks) may call them for you. Most of your components don't need to import or use them.

---

## Server APIs for Web Streams

These methods are only available in the environments with [Web Streams](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API), which includes browsers, Deno, and some modern edge runtimes:

* [`renderToReadableStream`](renderToReadableStream.md) renders a React tree to a [Readable Web Stream.](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream)
* [`resume`](renderToPipeableStream.md) resumes [`prerender`](../static/prerender.md) to a [Readable Web Stream](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream).

> [!note]
>
> Node.js also includes these methods for compatibility, but they are not recommended due to worse performance. Use the [dedicated Node.js APIs](#Server APIs for Node.js Streams) instead.
>

---

## Server APIs for Node.js Streams

These methods are only available in the environments with [Node.js Streams:](https://nodejs.org/api/stream.html)

* [`renderToPipeableStream`](renderToPipeableStream.md) renders a React tree to a pipeable [Node.js Stream.](https://nodejs.org/api/stream.html)
* [`resumeToPipeableStream`](renderToPipeableStream.md) resumes [`prerenderToNodeStream`](../static/prerenderToNodeStream.md) to a pipeable [Node.js Stream.](https://nodejs.org/api/stream.html)

---

## Legacy Server APIs for non-streaming environments

These methods can be used in the environments that don't support streams:

* [`renderToString`](renderToString.md) renders a React tree to a string.
* [`renderToStaticMarkup`](renderToStaticMarkup.md) renders a non-interactive React tree to a string.

They have limited functionality compared to the streaming APIs.
