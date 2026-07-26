# `excludeDirectories`

You can use [`excludeFiles`](excludeFiles.md) to drastically reduce the number of files which are watched during `--watch`. This can be a useful way to reduce the number of open file which TypeScript tracks on Linux.

```json
{
  "watchOptions": {
    "excludeDirectories": ["**/node_modules", "_build", "temp/*"]
  }
}
```
