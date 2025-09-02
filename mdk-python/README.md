mdk-python is an implementation of the MDK spec in Python, allowing MUGEN character developers to write their character code in Python.

mdk-python targets MTL for compilation, which is an existing language which implements the MDK spec. This is done to reduce the amount of effort required to implement the MDK spec.

This document provides an overview of how to use mdk-python to start developing a character. It assumes a little bit of familiarity with how to create characters using CNS.

## Compilation

mdk-python compilation is a 2-step process. It first compiles your Python code to MTL, which is an extension to the CNS language. Then the MTL compiler translates the code to CNS which can be used to run a character.

## Debugger

mdk-python generates MTL which is compatible with the MTL debugger. This means you can use the `mtldbg` command-line interface for debugging your character.

Refer to the documentation for `mtldbg` (`mtlcc/DEBUGGER.md`) to learn how to use the debugger. Run `info files` in the debugger to check which files you can set breakpoints on. You should be able to set breakpoints using your Python files and line numbers directly.

## Package Overview

The `mdk.compiler` package contains functions you will need to build your character, such as the `statedef`, `template`, `trigger`, and `statefunc` decorators, as well as the `build` function.

The `mdk.types` package contains type data you may need to build your character, as well as built-in variable types.

The `mdk.stdlib` package contains all of the state controllers, triggers, and redirects provided by CNS.

## Creating States

To create a state definition for your character, you need to use the `mdk.compiler.statedef` decorator. This decorator will register your state definition with the compiler. The compiler will process each state controller, template, or function you use in your state definition, and also interprets Python if statements into triggers.

A simple example of a state definition would look something like this:

```
from mdk.compiler import statedef
from mdk.stdlib import Null

@statedef()
def myCustomState():
    Null()
```

The `statedef` decorator accepts several optional parameters which would normally be applied to the Statedef block in CNS (see https://www.elecbyte.com/mugendocs/cns.html#details-on-statedef). For example, to set the movetype for your state definition:

```
from mdk.compiler import statedef
from mdk.stdlib import Null
from mdk.types import MoveType

@statedef(movetype = MoveType.A)
def myCustomState():
    Null()
```

This decorator also accepts several additional parameters, which are used to modify how the state will be compiled. 

- By default, the state will be assigned the next unused state number for your character. You can use the `stateno` parameter to specify a state number instead. This is useful if, for example, you want to override a common state and so you need to create a state with a specific ID.

```
from mdk.compiler import statedef
from mdk.stdlib import Null

@statedef(stateno = 0)
def myOverrideState():
    Null()
```

- The `scope` parameter is used to assign a scope to the state definition, which is a MTL/MDK concept. The scope of a state definition informs the compiler of what type of actor might be entering that state (e.g. player, helper, helper(id), or enemy/target). The compiler can then do optimizations related to variable usage, and also check your states for correctness based on what transitions are possible.

To use scopes, you can either specify a scope using the `mdk.types.StateScope` class, or use the built-in scopes `SCOPE_TARGET`, `SCOPE_PLAYER`, and `SCOPE_HELPER` from the same package.

```
from mdk.compiler import statedef
from mdk.stdlib import Null
from mdk.types import SCOPE_HELPER

my_helper_id = 1000

@statedef(scope = SCOPE_HELPER(my_helper_id))
def myHelperState():
    Null()
```

- The `mode` parameter is used to determine the trigger translation mode to use in the statedef. The default translation mode (`TranslationMode.STANDARD`) is sufficient for most cases; the variable translation mode (`TranslationMode.VARIABLE`) uses a more complicated translation method which increases file size and trigger count. The main difference is that the variable translation mode works better if you are modifying variables inside `if` conditionals which depend on those variables (so if you are seeing odd behaviour and you are doing something that sounds like this, you may want to try the variable mode).

Note that mixing translation modes between `statedef` and any `statefunc` or `template` called by that statedef is likely to break, so if your statedef uses any statefunc or template definitions, try to stick to STANDARD translation mode.

All of the built-in CNS triggers and state controllers are exposed in the `mdk.stdlib` package.

## Empty Expressions

Sometimes you will need to pass an empty value to a property for a state controller. For example, when you run a state definition with `hitdefpersist` set to `True`, you may want to run a `HitDef` with the `attr` property empty to unset a HitDef when it's no longer needed. In these cases, you can use `mdk.stdlib.EmptyExpression` and `mdk.stdlib.EmptyTuple`:

```
from mdk.compiler import statedef
from mdk.stdlib import HitDef, EmptyTuple

@statedef()
def myState():
    HitDef(attr = EmptyTuple)
```

## Creating Variables

In mdk-python, there is no need to use the `var` or `fvar` triggers or to remember variable indices. Instead you use the built-in variable classes to create variables. When MTL is compiling the output of your code, it assigns free variable indices to each variable you created.

In MUGEN, each actor (player/helper) gets its own set of variables, so if you use a global variable in two states (one run by a player, and one run by a helper) the variable value is not shared between the two.

mdk-python and MTL create a distinction between global and local variables. If you need to use a variable across several state definitions, it's smart to declare it in a global scope (i.e. outside of any state definition).

To create a global variable, simply declare it like this:

```
from mdk.types import IntVar

myVariable = IntVar()
```

Or use the VariableExpression form if you need more control over the variable type:

```
from mdk.types import ByteType, VariableExpression

myByteVariable = VariableExpression(ByteType)
```

To declare a local variable, use either of these forms from inside a state definition:

```
from mdk.compiler import statedef
from mdk.stdlib import Null
from mdk.types import IntVar

@statedef()
def myCustomState():
    myVar = IntVar()

    Null()
```

To update the value of a variable, you can use the `VarAdd`/`VarSet` controllers, or use the `add`/`set` functions on the variable itself:

```
from mdk.compiler import statedef
from mdk.stdlib import Null
from mdk.types import IntVar

@statedef()
def myCustomState():
    myVar = IntVar()

    if Time == 0: myVar.set(0)

    Null()

    VarAdd(var = myVar, value = 1)
```

## Print Statements

All `print` statements inside a function annotated with `@statedef` (as well as any functions annotated with `@statefunc` or `@template`) are automatically converted into DisplayToClipboard or AppendToClipboard functions.

You may specify some optional parameters to control the behaviour:

- Pass `append = True` to use AppendToClipboard instead of DisplayToClipboard in the generated MTL
- Pass `end = 'x'` where `x` is any string to set the end character for your statement

Additionally if you want to issue a `print` statement which is NOT converted into a clipboard controller (e.g. if you are trying to debug something which is happening during compilation), pass `compile = False` in your print statement.

So for example, the below code:

```
@statedef()
def myStatedef():
    local_myVar = IntVar()
    local_myFloat = FloatVar()

    print(f"myVar = {local_myVar} and myFloat = {local_myFloat}")
```

would be automatically converted into the following MTL:

```
[Statedef 1]
[State ]
type = DisplayToClipboard
trigger1 = true
text = "myVar = %d and myFloat = %f"
params = local_myVar, local_myFloat
```

## Using Redirects

Redirecting triggers is enabled by the redirect forms provided in the `mdk.stdlib` package. Each redirect is set up for you to access redirected triggers as a property. For example, to access `Time` on the `root` redirect:

```
from mdk.compiler import statedef
from mdk.stdlib import Null, root
from mdk.types import IntVar, SCOPE_HELPER

@statedef(scope = SCOPE_HELPER(1))
def myCustomState():
    myVar = IntVar()
    myVar.set(root.Time)
```

In CNS, certain redirects are set up to allow a free-standing form or a function form (for example, `enemy` and `enemy(0)`). In mdk-python, these have separate accessors; if you need to use the function form, add the `ID` suffix:

```
from mdk.compiler import statedef
from mdk.stdlib import Null, enemy, enemyID
from mdk.types import IntVar, SCOPE_HELPER

@statedef(scope = SCOPE_HELPER(1))
def myCustomState():
    myVar = IntVar()

    myVar.set(enemy.Time)

    myVar.set(enemyID(0).Time)
```

## Using Python Functions

It is possible to separate your logic into Python functions, for readability or reuse.

During compilation, mdk-python reads all of your functions marked with `@statedef` and interprets both the controllers and the triggers (if-statements) involved.

If you make a call to a bare Python function from a `statedef` function, the controllers you use in that function will still work, but your triggers will not be interpreted correctly. So for example, the below Python code:

```
from mdk.compiler import statedef
from mdk.stdlib import Null, Time

def separatedLogic():
    if Time == 0: Null()

@statedef()
def myCustomState():
    separatedLogic()
```

Would compile to this:

```
[Statedef 1]

[State ]
type = Null
trigger1 = 1
```

Note that the controller has `trigger1 = 1` instead of `trigger1 = Time == 0`.

To ensure your triggers in Python functions are parsed properly, you must use the `mdk.compiler.statefunc` decorator to register your function with the compiler:

```
from mdk.compiler import statedef, statefunc
from mdk.stdlib import Null, Time

@statefunc
def separatedLogic():
    if Time == 0: Null()

@statedef()
def myCustomState():
    separatedLogic()
```

## Building States

To run a build, use the `mdk.compiler.build` function:

```
from mdk.compiler import statedef, build
from mdk.stdlib import Null

@statedef()
def myCustomState():
    Null()

if __name__ == "__main__":
    build("Character.def", "Character.mtl")
```

You must pass the location of the `.def` file for your character, as well as the name of the file to write the intermediate MTL code to.

The `build` function also accepts optional keyword arguments:

- run_mtl: default True. if set to False, the compiler will not run the MTL compiler, and will only output your MTL intermediate file.
- skip_templates: default False. if set to True, the compiler will not build any templates.
- locations: default True. if set to False, the compiler will not include location debugging info (reduces file size).
- compress: default False. if set to True, the compiler will minimize the MTL intermediate file size.
- preserve_ir: default False. if set to True, the compiler will not delete the MTL intermediate file after running the MTL compiler.
- target_folder: default "mdk-out". specifies where to write the output of the MTL compilation.

## Using Templates

Templates are a MTL feature for creating reusable logic (similar to `@statefunc` functions above). Because mdk-python uses MTL as an intermediate step, you can also create templates in mdk-python.

The main purpose for this is if you want to create a library which can be used both by MTL developers and mdk-python developers.

To create a template, use the `mdk.compiler.template` decorator:

```
from mdk.compiler import template
from mdk.types import IntType, Expression

@template(inputs = [IntType], library = "libtest.inc")
def myTemplate(myInput: Expression):
    ...
```

The `@template` decorator accepts several optional parameters. If your template takes some inputs, they should have `Expression` type in your function definition, and you will declare the real type of the input in the `inputs` parameter to the decorator.

To specify the output library name, pass the `library` parameter. This can allow you to split your templates between multiple output files so they can be included separately.

You can also pass a function through the `validator` parameter. This parameter allows you to inspect and modify arguments passed to your template at build time. This can be useful for specifying default values for arguments. For example:

```
from mdk.compiler import template
from mdk.types import IntType, Expression

@template(inputs = [IntType], library = "libtest.inc", validator = myValidator)
def myTemplate(myInput: Expression):
    ...

def myValidator(myInput):
    if not isinstance(myInput, Expression) and myInput == None:
        return { "myInput": Expression(0, IntType) }
    return { "myInput": myInput }
```

## Using User-Defined Types

MTL also provides functionality for creating user-defined types. MTL supports several kinds of user-defined types, including aliases and unions; however these types are not super useful in mdk-python as the Python typing system provides support for union-ish types already.

However mdk-python does offer support for the MTL flag and enum types. Enum types are used to specify a value by name, which is useful if you want to avoid using magic numbers in your code. MTL will compile your user-defined enum and flag types into integers which are compatible with CNS.

For example, you can create a user-defined enum type as below. You specify a name for the type (which should generally match with the name you use for the Python variable that stores the type), as well as each member for the enum. You can also optionally specify an output library for the type definition to be written to.

```
from mdk.types import EnumType

MyEnumType = EnumType("MyEnumType", ["StartValue", "ValueOne", "ValueTwo"], library = "my_types.inc")
```

Using this type is simple; you can treat it as an integer in most places, and can also create, assign, and compare variables of this enum type.

```
from mdk.types import EnumType, VariableExpression

MyEnumType = EnumType("MyEnumType", ["StartValue", "ValueOne", "ValueTwo"], library = "my_types.inc")

@statedef()
def myState():
    myVar = VariableExpression(MyEnumType)

    myVar.set(MyEnumType.ValueOne)
```

In the emitted CNS, `myVar` would correspond to an integer variable, and it would be assigned a value of 1 (based on the index of `ValueOne` in the member list of the type).

## Building Templates

To build templates, use the `mdk.compiler.library` function. This function accepts a list of templates you want to compile, and outputs one or more include files which can then be used for MTL.

```
from mdk.compiler import template, library
from mdk.types import IntType, Expression

@template(inputs = [IntType], library = "libtest.inc")
def myTemplate(myInput: Expression):
    ...

if __name__ == "__main__":
    library([myTemplate], dirname="templates")
```