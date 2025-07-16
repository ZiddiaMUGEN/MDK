# MDK: Mugen Development Kit

A set of tools to aid creation of MUGEN character code.

MTL (MUGEN Template Language) is an extension to the CNS format. It enables the use of templates to extend base state controller functionality. There are several other features added by MTL which are discussed below.

MDK (MUGEN Development Kit) is a set of libraries which transpile code from a source language (e.g. Python) into MTL templates. The MTL templates are then compiled to produce valid CNS files for use with the character.

## MTL

MTL provides several features to aid and extend character creation. Although MTL is a complete language which you can write your character in, the main purpose of MTL is as an intermediate language for MDK implementations.

For details take a look at `mtlcc/README.md`.

- Type System
- Type Definitions
- Templating
- Structure Definitions
- Named Variables
- Constant Triggers

## MDK

Currently the only flavor of MDK available is mdk-python. Using this toolkit you can create character code written entirely in Python. You can also use Python constructs such as loops to simplify your code.

Take a look at `mdk/README.md` for more details.