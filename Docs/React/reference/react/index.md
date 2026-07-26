# React Reference Overview

This section provides detailed reference documentation for working with React. For an introduction to React, please visit the [Learn](../../learn/index.md) section.

The React reference documentation is broken down into functional subsections:

## React

Programmatic React features:

* [Hooks](hooks.md) - Use different React features from your components.
* [Components](components.md) - Built-in components that you can use in your JSX.
* [APIs](apis.md) - APIs that are useful for defining components.
* [Directives](../rsc/directives.md) - Provide instructions to bundlers compatible with React Server Components.

## React DOM

React DOM contains features that are only supported for web applications (which run in the browser DOM environment). This section is broken into the following:

* [Hooks](../react-dom/hooks/index.md) - Hooks for web applications which run in the browser DOM environment.
* [Components](../react-dom/components/index.md) - React supports all of the browser built-in HTML and SVG components.
* [APIs](../react-dom/index.md) - The `react-dom` package contains methods supported only in web applications.
* [Client APIs](../react-dom/client/index.md) - The `react-dom/client` APIs let you render React components on the client (in the browser).
* [Server APIs](../react-dom/server/index.md) - The `react-dom/server` APIs let you render React components to HTML on the server.
* [Static APIs](../react-dom/static/index.md) - The `react-dom/static` APIs let you generate static HTML for React components.

## React Compiler

The React Compiler is a build-time optimization tool that automatically memoizes your React components and values:

* [Configuration](../react-compiler/configuration.md) - Configuration options for React Compiler.
* [Directives](../react-compiler/directives.md) - Function-level directives to control compilation.
* [Compiling Libraries](../react-compiler/compiling-libraries.md) - Guide for shipping pre-compiled library code.

## ESLint Plugin React Hooks

The [ESLint plugin for React Hooks](../eslint-plugin-react-hooks/index.md) helps enforce the Rules of React:

* [Lints](../eslint-plugin-react-hooks/index.md) - Detailed documentation for each lint with examples.

## Rules of React

React has idioms — or rules — for how to express patterns in a way that is easy to understand and yields high-quality applications:

* [Components and Hooks must be pure](../rules/components-and-hooks-must-be-pure.md) – Purity makes your code easier to understand, debug, and allows React to automatically optimize your components and hooks correctly.
* [React calls Components and Hooks](../rules/react-calls-components-and-hooks.md) – React is responsible for rendering components and hooks when necessary to optimize the user experience.
* [Rules of Hooks](../rules/rules-of-hooks.md) – Hooks are defined using JavaScript functions, but they represent a special type of reusable UI logic with restrictions on where they can be called.

## Legacy APIs

* [Legacy APIs](legacy.md) - Exported from the `react` package, but not recommended for use in newly written code.
