# Static React DOM APIs

The `react-dom/static` APIs let you generate static HTML for React components. They have limited functionality compared to the streaming APIs. A [framework](../../../learn/creating-a-react-app.md#Full-stack frameworks) may call them for you. Most of your components don't need to import or use them.

---

## Static APIs for Web Streams

These methods are only available in the environments with [Web Streams](https://developer.mozilla.org/en-US/docs/Web/API/Streams_API), which includes browsers, Deno, and some modern edge runtimes:

* [`prerender`](prerender.md) renders a React tree to static HTML with a [Readable Web Stream.](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream)
* (Experimental)  [`resumeAndPrerender`](resumeAndPrerender.md) continues a prerendered React tree to static HTML with a [Readable Web Stream](https://developer.mozilla.org/en-US/docs/Web/API/ReadableStream).

Node.js also includes these methods for compatibility, but they are not recommended due to worse performance. Use the [dedicated Node.js APIs](#Static APIs for Node.js Streams) instead.

---

## Static APIs for Node.js Streams

These methods are only available in the environments with [Node.js Streams](https://nodejs.org/api/stream.html):

* [`prerenderToNodeStream`](prerenderToNodeStream.md) renders a React tree to static HTML with a [Node.js Stream.](https://nodejs.org/api/stream.html)
* (Experimental)  [`resumeAndPrerenderToNodeStream`](resumeAndPrerenderToNodeStream.md) continues a prerendered React tree to static HTML with a [Node.js Stream.](https://nodejs.org/api/stream.html)
