# MTL - MDK Implementation

This document describes the progress towards implementation of the MDK spec and the syntax involved in each component of the spec.

## Implementation Status

1. CNS Compatibility - partially implemented; trigger redirection is not implemented.
2. Type System - partially implemented
    - Built-in types - partially implemented; `char` type is not implemented.
    - Tuples, Optionals, and Repeated Types - partially implemented; user-defined triggers and template parameters cannot use `tuples` or `optionals`.
    - Custom Types - partially implemented; `struct` member access is not implemented.
    - Type Conversion Rules - partially implemented; builtins for enum/flag conversion not implemented.
3. Template Definitions - fully implemented, without granular scopes (locals are hoisted)
4. Trigger Definitions - user-defined fully implemented; special types partially implemented
    - Operator Triggers - partially implemented; builtin operator triggers are supposed but users cannot define operator triggers
5. Named State Definitions - not implemented
6. Named Variables - partially implemented; cannot specify system variables
    - Variable Scope and Initialization - partially implemented (+ persistence)
7. Character Resource References - not implemented
8. State Controller Repetition (Loops) - not implemented
9. State Definition Scope - not implemented
10. Constant Triggers - partially implemented; a small number of builtins are implemented

## Syntax

### 2. Type System

Creating a new type definition uses the `Define Type` block, which is defined below.

```
[Define Type]
name = TYPE NAME: string
type = TYPE CATEGORY (union, alias, enum, flag)
```

The `Define Type` block accepts additional parameters depending on the value of `type`. See the sections below for each category.

#### Alias Types

For `type = alias`, specify exactly one `source` parameter naming a type to map this type to.
    - If no `source` parameter is provided, translation throws an error.
    - If the source type does not exist, translation throws an error.

#### Union Types

For `type = union`, specify one or more `member` parameters naming a type to include in the union.
    - If no `member` parameters are specified, translation throws an error.
    - If the `member` types do not have the same size, translation throws an error.
    - If any source type does not exist, translation throws an error.

#### Enumeration Types

For `type = enum`, specify one or more `enum` parameters naming the enumeration constant.
    - If no `enum` parameters are specified, translation throws an error.
    - If duplicate `enum` values are specified, translation throws an error.

When referencing an enumeration constant in a context where the type is not explicit, specify `EnumName.EnumConstant`. For example, you can use `MoveTypeEnum.A` for an attack statedef.
    - This applies only when the type is not clear, e.g. when calling `etoi` with an enumeration constant. Calling `etoi(A)` will fail as A cannot be resolved from type information available; calling `etoi(MoveTypeEnum.A)` will pass.
    - If the type is clear, the enum name can be omitted. For example, when providing `movetype` in the Statedef block, `movetype = A` is fine as `typeof(movetype) == MoveType`.

#### Flag Types

For `type = flag`, specify one or more `flag` parameters naming the enumeration constant.
    - If no `flag` parameters are specified, translation throws an error.
    - If duplicate `flag` values are specified, translation throws an error.

References to Flag constants follow the same rules as references to Enum constants.

#### Structure Types

Structures have a specific syntax for declaration:

```
[Define Structure]
name = STRUCTURE NAME

[Define Members]
MEMBER NAME = MEMBER TYPE
```

Structures may specify as many members as they desire. Structure initialization can be done via VarSet:

```
[State ]
type = VarSet
trigger1 = 1
VARIABLE NAME = STRUCTURE_NAME(MEMBER1, MEMBER2, MEMBER3)
```

as well as inline:

```
[State ]
type = Null
trigger1 = myStructure := STRUCTURE_NAME(MEMBER1, MEMBER2, MEMBER3)
```

Structure fields can be accessed with a space. This aligns with existing access to 'members' in `Vel`, `Pos`, etc.

```
[State ]
type = Null
trigger1 = myStructure MEMBER1 = 1
```

### 3. Template Definitions

Developers can create reusable templates with parameters for input.

```
[Define Template]
name = TEMPLATE NAME: string

[Define Parameters]
PARAMETER NAME = PARAMETER TYPE

[State ]
type = Null
trigger1 = param0 = 1
```

For each parameter, the compiler will emit an error if the type is not known. Templates can then be used throughout regular statedefs:

```
[Statedef 0]

[State ]
type = TEMPLATE NAME
trigger1 = Alive
PARAMETER NAME = PARAMETER VALUE
```

Triggers provided when calling a template must be translated into triggers on the states comprising the template. The compiler may need to collapse triggers to be able to integrate them with triggers inside the template.

Templates are permitted to make use of local variables defined in the `Define Template` section.

The `Include` section can be used to import templates from an external file:

```
[Include]
source = FOLDER PATH/FILE PATH
import = TEMPLATE NAME
namespace = NAMESPACE NAME
```

The `import` property can optionally be specified one or more times, and can be used to import only specified template definitions from the file.

The `namespace` property is optional and can be used to prefix imported templates with a namespace. Using this, imported templates can be referenced as `NAMESPACE.TEMPLATE`.

The compiler will emit an error if the namespace is already defined, if the imported template is already defined, or if the file does not exist.

### 4. Trigger Definitions

MTL supports defining custom trigger functions to improve code readability. The `Define Trigger` section is used for this.

```
[Define Trigger]
name = MY TRIGGER
type = OUTPUT TYPE
value = TRIGGER EXPRESSION

[Define Parameters]
PARAMETER NAME = PARAMETER TYPE
```

To give a real-world example which provides a `max` function:

```
[Define Trigger]
name = max
type = numeric
value = ifelse(val1 > val2, val1, val2)

[Define Parameters]
val1 = numeric
val2 = numeric
```

MTL supports trigger overloading, which means two triggers can have the same name, so long as their parameter types are different. So for example, the below is legal (and allows use of concrete types instead of the `numeric` union):

```
[Define Trigger]
name = max
type = int
value = ifelse(val1 > val2, val1, val2)

[Define Parameters]
val1 = int
val2 = int

[Define Trigger]
name = max
type = float
value = ifelse(val1 > val2, val1, val2)

[Define Parameters]
val1 = float
val2 = float
```

### 6. Named Variables / Variable Scope and Initialization

TODO: put some documentation about how to declare globals. Declaring locals is made explicit already.

In MTL, variable scopes are supported. This allows for tighter variable usage as variables which are temporary to a state can be freed when the state is exited. At the moment, MTL only supports the global and state-local scopes, but may support granular scopes in the future.

By default, variables are considered global for compatibility with CNS, and are defined 'by usage' (i.e. simply assign a variable to a name and the compiler will infer its type and register it as a global).

To define a state-local variable, it can be specified in the Statedef section:

```
[Statedef 0]
type = S
local = VARIABLE NAME = VARIABLE TYPE
```

Multiple `local` definitions can be provided here. In some cases you may need to persist a local variable between two states. Take this for example, which is an attack providing a 10-frame window to input another command before returning to Idle:

```
[Statedef 200]
type = S
movetype = A
local = attackType = int

[State ]
type = VarSet
trigger1 = Command = "a"
attackType = 1

[State ]
type = VarSet
trigger1 = Command = "b"
attackType = 2

[State ]
type = ChangeState
trigger1 = attackType != 0
value = 201

[State ]
type = ChangeState
trigger1 = Time > 10
value = 0
```

The variable attackType is specific to this attack, so it makes sense to declare it as local. However the followup state 201 will not have access to this variable. Pass the local through in the ChangeState `persist` property. MTL will identify this and ensure the slot used by the local is not overwritten in the next state.

```
[State ]
type = ChangeState
trigger1 = attackType != 0
value = 201
persist = attackType
```

You must also specify attackType as a local in the followup state (201). The compiler will emit an error if a variable is persisted but not redeclared as local. MTL also permits setting default values for locals on state entry:

```
[Statedef 200]
type = S
movetype = A
local = attackType = int(0)
```

MTL will ensure the variable `attackType` is initialized to 0 at Time=0. If the state is recursive or re-entered, the variable WILL be re-initialized.