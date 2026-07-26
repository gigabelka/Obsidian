# `synchronousWatchDirectory`

Synchronously call callbacks and update the state of directory watchers on platforms that don`t support recursive watching natively. Instead of giving a small timeout to allow for potentially multiple edits to occur on a file.

```json
{
  "watchOptions": {
    "synchronousWatchDirectory": true
  }
}
```
