# MTL Debugger Extension

This extension provides a debugging interface for MUGEN characters (including regular CNS-based characters, as well as MTL/MDK characters).

The debugger allows you to place breakpoints, inspect variables and trigger values, and step through your code.

## Using the Debugger

1. Install the `MUGEN Debugger` extension in VS code.
2. Install the `mtl-mugen` Python library locally or in a virtual environment via pip: `python -m pip install mtl-mugen`
3. Open your character folder in vscode and create a new debugging configuration at `.vscode/launch.json`. You can use the `MUGEN Debug: Launch` template, or follow the template below:

```
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "mtldbg",
      "request": "launch",
      "name": "Debug in MDK",
      "program": "${workspaceFolder}/CharacterName.def",
      "database": "${workspaceFolder}/CharacterName.mdbg",
      "pythonPath": "python",
      "mugenPath": "/path/to/mugen.exe",
      "stopOnEntry": true,
      "build": false,
      "generate": true
    }
  ]
}
```

- The `build` option will run a MTL/MDK build before launch if set to `true`. If you are debugging a CNS-based character, you can leave this set to `false`.
- The `generate` option is used with CNS-based characters to generate a debugging database before launch. If you are debugging a CNS-based character, you **must** set this to `true`. Otherwise, leave it set to `false`.

4. Open the Debug view in vscode and run the debugger. The debugger will pause automatically when MUGEN is ready to launch; hit the play button at the top of the screen to continue launching the game.