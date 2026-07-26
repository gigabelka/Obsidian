# React DOM APIs

The `react-dom` package contains methods that are only supported for the web applications (which run in the browser DOM environment). They are not supported for React Native.

---

## APIs

These APIs can be imported from your components. They are rarely used:

* [`createPortal`](createPortal.md) lets you render child components in a different part of the DOM tree.
* [`flushSync`](flushSync.md) lets you force React to flush a state update and update the DOM synchronously.

## Resource Preloading APIs

These APIs can be used to make apps faster by pre-loading resources such as scripts, stylesheets, and fonts as soon as you know you need them, for example before navigating to another page where the resources will be used.

[React-based frameworks](../../learn/creating-a-react-app.md) frequently handle resource loading for you, so you might not have to call these APIs yourself. Consult your framework's documentation for details.

* [`prefetchDNS`](prefetchDNS.md) lets you prefetch the IP address of a DNS domain name that you expect to connect to.
* [`preconnect`](preconnect.md) lets you connect to a server you expect to request resources from, even if you don't know what resources you'll need yet.
* [`preload`](preload.md) lets you fetch a stylesheet, font, image, or external script that you expect to use.
* [`preloadModule`](preloadModule.md) lets you fetch an ESM module that you expect to use.
* [`preinit`](preinit.md) lets you fetch and evaluate an external script or fetch and insert a stylesheet.
* [`preinitModule`](preinitModule.md) lets you fetch and evaluate an ESM module.

---

## Entry points

The `react-dom` package provides two additional entry points:

* [`react-dom/client`](client/index.md) contains APIs to render React components on the client (in the browser).
* [`react-dom/server`](server/index.md) contains APIs to render React components on the server.

---

## Removed APIs

These APIs were removed in React 19:

* [`findDOMNode`](https://18.react.dev/reference/react-dom/findDOMNode): see [alternatives](https://18.react.dev/reference/react-dom/findDOMNode#alternatives).
* [`hydrate`](https://18.react.dev/reference/react-dom/hydrate): use [`hydrateRoot`](client/hydrateRoot.md) instead.
* [`render`](https://18.react.dev/reference/react-dom/render): use [`createRoot`](client/createRoot.md) instead.
* [`unmountComponentAtNode`](https://react.dev/reference/react-dom/unmountComponentAtNode): use [`root.unmount()`](client/createRoot.md#`root.unmount%28%29`) instead.
* [`renderToNodeStream`](https://18.react.dev/reference/react-dom/server/renderToNodeStream): use [`react-dom/server`](server/index.md) APIs instead.
* [`renderToStaticNodeStream`](https://18.react.dev/reference/react-dom/server/renderToStaticNodeStream): use [`react-dom/server`](server/index.md) APIs instead.
