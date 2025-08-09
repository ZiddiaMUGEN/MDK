## Usage

- Use the `@statedef` annotation to create your state definitions. Use controllers and triggers inside your state definition to build your character logic.
- Use the `IntVar`, `FloatVar`, and `BoolVar` types to create local and global variable definitions. By default, a variable declared inside a `@statedef` function is local, and variables declared outside of a `@statedef` function are global.
- Use the `@template` annotation to create reusable MTL templates. When you generate your character, all templates will be added to source files and included in your main state file.
- Use `build` to build your character's states, and `library` to build specified templates to a MTL library include file.

## Implementation Progress

### 1. Basic logic

- Statedef annotation - IMPLEMENTED
    - Python functions can have the `@statedef` annotation to mark them for inclusion in the output file.
    - `@statedef` must accept optional statedef keyword parameters.
    - `@statedef` must optionally accept state number and output file parameters.

- Statedef calls - IMPLEMENTED
    - calls to functions annotated with `@statedef` must be converted to ChangeState controllers.

- Statedef output - PARTIALLY IMPLEMENTED

- Variable declaration/assignment - PARTIALLY IMPLEMENTED
    - During annotation processing a list of variables used by the state must be generated.
    - Unique IDs must be assigned to each variable.
    - variables cannot be default-initialized on state entry, this is something to consider later.

- If conversion - IMPLEMENTED
    - Any `if` statement in the statedef is converted to use Expression types.
    - `else` and `elif` are converted to separate `if` statements with negations of the parent `if`'s statement.

### 2. CNS constructs

- State controller definitions, typing - IN PROGRESS

### 3. MTL constructs

- Import from MTL include file - NOT STARTED
    - Make use of MTL include functionality to import directly from `inc` files.
    - Convert any MTL templates into Python functions.

- MTL template annotation - NOT STARTED
    - Python functions can have the `@template` annotation to mark them for inclusion in a template file.
    - `@template` must accept a mandatory output file parameter
    - Output files from `@template` need to be usable in an external MTL project.

### 4. Checks and lints

- Compile-time/runtime variable lint - NOT STARTED