# `disableFilenameBasedTypeAcquisition`

TypeScript's type acquisition can infer what types should be added based on filenames in a project. This means that having a file like `jquery.js` in your project would automatically download the types for JQuery from DefinitelyTyped.

You can disable this via `disableFilenameBasedTypeAcquisition`.

```json
{
  "typeAcquisition": {
    "disableFilenameBasedTypeAcquisition": true
  }
}
```
