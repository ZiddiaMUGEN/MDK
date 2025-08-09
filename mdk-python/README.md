mdk-python is an implementation of the MDK spec in Python, allowing MUGEN character developers to write their character code in Python.

mdk-python targets MTL for compilation, which is an existing language which implements the MDK spec. This is done to reduce the amount of effort required to implement the MDK spec.

## Usage

### Building

When you have created your character file, run `mdk.compiler.build()` to build to a MTL source file.

If you are building a MTL library instead, run `mdk.compiler.library()` to create a MTL include file. You must also specify which templates and types to add to the include library.

### Type Definitions

MDK support type definitions using the `mdk.types.TypeSpecifier` type. To create a new type definition, you should use one of the type specifier factories provided in this module.

### State Definitions

A Python function can be annotated with `@statedef` to specify the function creates a state definition. The @statedef annotation accepts a variety of parameters to set values for the statedef, such as the state ID.

