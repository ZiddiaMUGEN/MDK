Python implementation of the MDK enabling developers to write MUGEN character code in a higher-level language.

How it works:

- The user creates state definitions using the `@statedef` decorator
- The decorator maps the statedef name to the input function, saves the original function definition, and remaps any calls to it to `ChangeState`
- When `mdk.build` is called, the list of mapped statedefs is iterated to build the final state list.

TODO: Support a `@template` decorator for functions which are reusable.
This is not essential (a function call in Python will just end up incorporating code from the function into the current statedef) but it can help the generated tMUGEN to be more readable by using custom controllers instead of inlining directly.