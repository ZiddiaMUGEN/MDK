# MTL: MUGEN Template Language

MTL provides an extension to the CNS language, used to create characters in the fighting game engine MUGEN. The tooling in the mtl-mugen package can be used to compile and debug character code written in CNS with MTL extensions.

Some features provided by MTL include:

- Named variables
- Named state definitions
- Trigger definitions (for code reuse)
- Template definitions (for code reuse)
- Custom type system and type checking

For more details on syntax and usage, take a look at the specification in [this document](https://github.com/ZiddiaMUGEN/MDK/blob/main/mtlcc/SPEC.md).

This package provides two scripts which are related to MUGEN character development. The `mtlcc` script is used to compile MTL character code to CNS; the `mtldbg` script is used to run a character compiled by `mtlcc` in debugging mode. Take a look at [this document](https://github.com/ZiddiaMUGEN/MDK/blob/main/mtlcc/DEBUGGER.md) for more details on how to use the debugger.

## Basic Usage

In order to compile a character with `mtlcc`, you should prepare a `.def` file describing your character. Because MTL only handles character code, you must prepare the AIR, SFF, SND, commands, and constants (`[Data]`, `[Movement]`, etc.) in separate files as you would for a standard MUGEN character. Take a look at the `.def` file in [this folder](https://github.com/ZiddiaMUGEN/MDK/tree/main/mtlcc/sample/UnitTest) for an example of how this is set up.

Inside the `.def` file, you should specify the files for your MTL character code as you normally would (i.e. add them with keys `st`, `st1`, ... in the `[Files]` section). `mtlcc` can handle up to 1000 input state files (compared to CNS which supports up to 10 with `st9`). You may also specify state definitions inside your command file.

When your code is ready to compile, you can run the compiler: `mtlcc <input path> <output path>`. The `input path` should be the path to the `.def` file, and the `output path` should specify a folder to place the compiled character files into. For example, `mtlcc ./sample/UnitTest/UnitTest.def ./sample/UnitTest/UnitTest.CNS/`.