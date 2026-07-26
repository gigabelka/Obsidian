# Installation

This guide will help you install and configure React Compiler in your React application.

* How to install React Compiler
* Basic configuration for different build tools
* How to verify your setup is working

## Prerequisites

React Compiler is designed to work best with React 19, but it also supports React 17 and 18. Learn more about [React version compatibility](../../reference/react-compiler/target.md).

## Installation

Install React Compiler as a `devDependency`:

```bash
npm install -D babel-plugin-react-compiler@latest
```

Or with Yarn:

```bash
yarn add -D babel-plugin-react-compiler@latest
```

Or with pnpm:

```bash
pnpm install -D babel-plugin-react-compiler@latest
```

## Basic Setup

React Compiler is designed to work by default without any configuration. However, if you need to configure it in special circumstances (for example, to target React versions below 19), refer to the [compiler options reference](../../reference/react-compiler/configuration.md).

The setup process depends on your build tool. React Compiler includes a Babel plugin that integrates with your build pipeline.

> [!warning] Pitfall
> React Compiler must run **first** in your Babel plugin pipeline. The compiler needs the original source information for proper analysis, so it must process your code before other transformations.

### Babel

Create or update your `babel.config.js`:

```js
module.exports = {
  plugins: [
    'babel-plugin-react-compiler', // must run first!
    // ... other plugins
  ],
  // ... other config
};
```

### Vite

If you use Vite with version 6.0.0 or later of `@vitejs/plugin-react`, you can use the `reactCompilerPreset`:

```bash
npm install -D @rolldown/plugin-babel
```

```js
// vite.config.js
import { defineConfig } from 'vite';
import react, { reactCompilerPreset } from '@vitejs/plugin-react';
import babel from '@rolldown/plugin-babel';

export default defineConfig({
  plugins: [
    react(),
    babel({
      presets: [reactCompilerPreset()]
    }),
  ],
});
```

> [!note]
> In `@vitejs/plugin-react@6.0.0`, the inline Babel option was removed. If you're using an older version, you can use:
>
> ```js
> // vite.config.js
> import { defineConfig } from 'vite';
> import react from '@vitejs/plugin-react';
>
> export default defineConfig({
>   plugins: [
>     react({
>       babel: {
>         plugins: ['babel-plugin-react-compiler'],
>       },
>     }),
>   ],
> });
> ```

Alternatively, you can use the Babel plugin directly with `@rolldown/plugin-babel`:

```js
// vite.config.js
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import babel from '@rolldown/plugin-babel';

export default defineConfig({
  plugins: [
    react(),
    babel({
      plugins: ['babel-plugin-react-compiler'],
    }),
  ],
});
```

### Next.js

Please refer to the [Next.js docs](https://nextjs.org/docs/app/api-reference/next-config-js/reactCompiler) for more information.

### React Router
Install `vite-plugin-babel`, and add the compiler's Babel plugin to it:

```bash
npm install vite-plugin-babel
```

```js
// vite.config.js
import { defineConfig } from "vite";
import babel from "vite-plugin-babel";
import { reactRouter } from "@react-router/dev/vite";

const ReactCompilerConfig = { /* ... */ };

export default defineConfig({
  plugins: [
    reactRouter(),
    babel({
      filter: /\.[jt]sx?$/,
      babelConfig: {
        presets: ["@babel/preset-typescript"], // if you use TypeScript
        plugins: [
          ["babel-plugin-react-compiler", ReactCompilerConfig],
        ],
      },
    }),
  ],
});
```

### Webpack

A community webpack loader is [now available here](https://github.com/SukkaW/react-compiler-webpack).

### Expo

Please refer to [Expo's docs](https://docs.expo.dev/guides/react-compiler/) to enable and use the React Compiler in Expo apps.

### Metro (React Native)

React Native uses Babel via Metro, so refer to the [Usage with Babel](#Babel) section for installation instructions.

### Rspack

Please refer to [Rspack's docs](https://rspack.dev/guide/tech/react#react-compiler) to enable and use the React Compiler in Rspack apps.

### Rsbuild

Please refer to [Rsbuild's docs](https://rsbuild.dev/guide/framework/react#react-compiler) to enable and use the React Compiler in Rsbuild apps.

## ESLint Integration

React Compiler includes an ESLint rule that helps identify code that can't be optimized. When the ESLint rule reports an error, it means the compiler will skip optimizing that specific component or hook. This is safe: the compiler will continue optimizing other parts of your codebase. You don't need to fix all violations immediately. Address them at your own pace to gradually increase the number of optimized components.

Install the ESLint plugin:

```bash
npm install -D eslint-plugin-react-hooks@latest
```

If you haven't already configured eslint-plugin-react-hooks, follow the [installation instructions in the readme](https://github.com/react/react/blob/main/packages/eslint-plugin-react-hooks/README.md#installation). The compiler rules are available in the `recommended-latest` preset.

The ESLint rule will:
- Identify violations of the [Rules of React](../../reference/rules/index.md)
- Show which components can't be optimized
- Provide helpful error messages for fixing issues

## Verify Your Setup

After installation, verify that React Compiler is working correctly.

### Check React DevTools

Components optimized by React Compiler will show a "Memo ✨" badge in React DevTools:

1. Install the [React Developer Tools](../react-developer-tools.md) browser extension
2. Open your app in development mode
3. Open React DevTools
4. Look for the ✨ emoji next to component names

If the compiler is working:
- Components will show a "Memo ✨" badge in React DevTools
- Expensive calculations will be automatically memoized
- No manual `useMemo` is required

### Check Build Output

You can also verify the compiler is running by checking your build output. The compiled code will include automatic memoization logic that the compiler adds automatically.

```js
import { c as _c } from "react/compiler-runtime";
export default function MyApp() {
  const $ = _c(1);
  let t0;
  if ($[0] === Symbol.for("react.memo_cache_sentinel")) {
    t0 = <div>Hello World</div>;
    $[0] = t0;
  } else {
    t0 = $[0];
  }
  return t0;
}

```

## Troubleshooting

### Opting out specific components

If a component is causing issues after compilation, you can temporarily opt it out using the `"use no memo"` directive:

```js
function ProblematicComponent() {
  "use no memo";
  // Component code here
}
```

This tells the compiler to skip optimization for this specific component. You should fix the underlying issue and remove the directive once resolved.

For more troubleshooting help, see the [debugging guide](debugging.md).

## Next Steps

Now that you have React Compiler installed, learn more about:

- [React version compatibility](../../reference/react-compiler/target.md) for React 17 and 18
- [Configuration options](../../reference/react-compiler/configuration.md) to customize the compiler
- [Incremental adoption strategies](incremental-adoption.md) for existing codebases
- [Debugging techniques](debugging.md) for troubleshooting issues
- [Compiling Libraries guide](../../reference/react-compiler/compiling-libraries.md) for compiling your React library
