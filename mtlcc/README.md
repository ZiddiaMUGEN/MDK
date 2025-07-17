# MTL Standard

This document defines the extensions provided by MTL over CNS and how they are implemented. It also notes any warnings or errors MTL is expected to emit during translation.

This document provides minimal implementation details, it only notes the language changes.

## 1. Type System

- In CNS, there are only 2 fundamental variable types (`int` and `float`) which are implicitly convertible with one another.
    - There are also some value types (e.g. `string` and simple enumeration types for HitDefAttr, etc.) which cannot be stored in variables but are relevant at runtime.
- In MTL, several additional numeric types are offered and more powerful type checking is enabled. Please see the section for `Type Definitions` for details on each of these categories.
    - MTL supports the following **fundamental types**: 32-bit `int`, 32-bit `float`, 16-bit `short`, 8-bit `byte`, 8-bit `char`, 8-bit `bool8`, 1-bit `bool`
    - MTL also supports the following **union types**: `numeric` = `union(int, float)`.
    - MTL also supports the following **enumeration types**: `StateType`, `MoveType`, `PhysicsType`, `Transparency`, `AssertSpecialFlag`
    - MTL also supports the following **flag types**: `HitDefAttr`
- MTL also exposes several types for working with the compiler:
    - `Type`: an alias for `integer` which can also be used to retrieve type information from the compiler.
    - `Enum`: an alias for `Type` which is scoped specifically to enumeration types.
    - `Flag`: an alias for `Type` which is scoped specifically to flag types.

- For included CNS files, variable types are inferred to be `numeric`.

### 1.1 Type Conversion

- MTL supports several flavors of **type conversion**. Several conversions can be done automatically (though they may emit an error).

- For the builtin types:
    - `int` is implicitly convertible to `float`.
    - `float` cannot be implicitly converted to `int` as it results in loss of precision.
    - smaller builtin types can implicitly convert to wider ones (`bool`->`byte`->`short`->`int`)
    - `char` is implicitly convertible to `byte`, but the reverse is not true.

- And in general for defined types:
    - `alias` types are resolved to their source type.
    - `enum` can be converted to `int` via builtin functions, and vice versa.
    - `flag` can be converted to `int` via builtin functions, and vice versa.
    - single `flag` values can also be converted to `bool`  via builtin functions.

- Specifically for union types:
    - the union is always assumed to be the wider type during conversion.
    - in both conversions (type->union and union->type), it should be permitted if the type is a member of the union. the output is the union type.

## 2. Type Definitions

- In MTL, the type system also enables users to create **user-defined types**. User defined types can fall into one of several categories.
- Creating a new type definition uses the `Define Type` block, which is defined below.

```
[Define Type]
name = TYPE NAME: string
type = TYPE CATEGORY (union, alias, enum, flag)
```

- The `Define Type` block accepts additional parameters depending on the value of `type`. See the sections below for each category.

### 2.1. Alias Types

- Alias types map one type name to another. This is mostly just for convenience so e.g. if there is a very long type name, a shortname can be used instead.
- Alias types behave mostly identically to the source type. Most of the builtin constant triggers will map to the value of the source type. See `Builtin Constant Triggers` for details.
- For `type = alias`, specify exactly one `source` parameter naming a type to map this type to.
    - If no `source` parameter is provided, translation throws an error.
    - If the source type does not exist, translation throws an error.

### 2.2. Union Types

- Union types allow use of a single type name to refer to variables of different types.
- This can be used in cases where the concrete type is not known or does not matter (e.g. `numeric` is a union of `int` and `float` and can be used to get CNS-like typing for state controller parameters).
- For `type = union`, specify one or more `member` parameters naming a type to include in the union.
    - If no `member` parameters are specified, translation throws an error.
    - If the `member` types do not have the same size, translation throws an error.
    - If any source type does not exist, translation throws an error.

### 2.3 Enumeration Types

- Enumeration types provide a mapping from names to integer values. They can be used to improve readability of code.
- Enumerations are internally represented as integers. Conversions between enums and integers are provided in the built-in constant triggers.
- There are several built-in string enumerations which are used for state controllers. (For example, `movetype` in the Statedef block accepts a `MoveTypeEnum` value).
    - For string-type enumerations, the compiler must preserve the value and output it as a string, rather than an integer.
    - There is no facility for user-defined string-type enumerations as CNS cannot support the syntax.
- When referencing an enumeration constant in a context where the type is not explicit, specify `EnumName.EnumConstant`. For example, you can use `MoveTypeEnum.A` for an attack statedef.
    - This applies only when the type is not clear, e.g. when calling `etoi` with an enumeration constant. Calling `etoi(A)` will fail as A cannot be resolved from type information available; calling `etoi(MoveTypeEnum.A)` will pass.
    - If the type is clear, the enum name can be omitted. For example, when providing `movetype` in the Statedef block, `movetype = A` is fine as `typeof(movetype) == MoveTypeEnum`.
- For `type = enum`, specify one or more `enum` parameters naming the enumeration constant.
    - If no `enum` parameters are specified, translation throws an error.
    - If duplicate `enum` values are specified, translation throws an error.

### 2.4 Flag Types

- Flag types provide a mapping from names to integer values. They can be used to improve readability of code.
- Flag types are similar to enumerations, but one flag variable can represent more than one flag constant.
- For example, the `HitDefAttrFlag` type is a Flag type. When specifying a `HitDefAttr`, multiple constants can be provided, e.g. `SCA`.
- Flags are internally represented as bitflags. This means a maximum of 32 unique flag values can be supported.
- There are several built-in string flags which are used for state controllers. (For example, `hitdefattr` in the HitDef state controller accepts a `HitDefAttrFlag` value as part of its tuple).
    - For string-type flags, the compiler must preserve the value and output it as a string, rather than an integer.
    - There is no facility for user-defined string-type flags as CNS cannot support the syntax.
- References to Flag constants follow the same rules as references to Enum constants.
- For `type = flag`, specify one or more `flag` parameters naming the enumeration constant.
    - If no `flag` parameters are specified, translation throws an error.
    - If duplicate `flag` values are specified, translation throws an error.

### 2.5 Tuples

- Tuples provide a convenient way to group related values together.
- Although the CNS engine makes use of tuples, tuple types are not recommended to be used in MTL. Structures are the recommended option for grouping values.

## 3. Template Definitions

### 3.1 Define Template

- In MTL, developers can create reusable templates with parameters for input.

```
[Define Template]
name = TEMPLATE NAME: string

[Define Parameters]
PARAMETER NAME = PARAMETER TYPE

[State ]
type = Null
trigger1 = param0 = 1
```

- For each parameter, the compiler will emit an error if the type is not known.
- Templates can then be used throughout regular statedefs:

```
[Statedef 0]

[State ]
type = TEMPLATE NAME
trigger1 = Alive
PARAMETER NAME = PARAMETER VALUE
```

- Triggers provided when calling a template must be translated into triggers on the states comprising the template. The compiler may need to collapse triggers to be able to integrate them with triggers inside the template.

### 3.2 Include

- The `Include` section can be used to import templates from an external file:

```
[Include]
source = FOLDER PATH/FILE PATH
import = TEMPLATE NAME
namespace = NAMESPACE NAME
```

- The `import` property can optionally be specified one or more times, and can be used to import only specified template definitions from the file.
- The `namespace` property is optional and can be used to prefix imported templates with a namespace. Using this, imported templates can be referenced as `NAMESPACE.TEMPLATE`.
- The compiler will emit an error if the namespace is already defined, if the imported template is already defined, or if the file does not exist.

## 4. Trigger Definitions

- MTL supports defining custom trigger functions to improve code readability. The `Define Trigger` section is used for this.

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

## 5. Structure Definitions

- MTL supports defining structures as a grouping of related variables. 

```
[Define Structure]
name = STRUCTURE NAME

[Define Members]
MEMBER NAME = MEMBER TYPE
```

- Structures may specify as many members as they desire.
- Structure initialization can be done via VarSet:

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

- Structure fields can be accessed using the `.` operator:

```
[State ]
type = Null
trigger1 = myStructure.MEMBER1 = 1
```

## 6. Variable Scope and Initialization

- In CNS, because variables are just an array of numerics, there is no scoping rules for variables.
- In MTL, variable scopes are supported. This allows for tighter variable usage as variables which are temporary to a state can be freed when the state is exited.
- The compiler must maintain a list of what variables are 'in-scope' for each state definition.
- There are only 2 scopes (global and state-local) as any more granular scopes are very difficult to reason about in MTL.
    - This may need to be revisited (maybe with some operator to define a temporary scope for variables) since complicated template inclusions can easily run up the variable space if they are hoisted to the top level.

- By default, variables are considered global for compatibility with CNS.
- To define a state-local variable, it can be specified in the Statedef section:

```
[Statedef 0]
type = S
local = VARIABLE NAME
```

- Multiple `local` definitions can be provided here.
- In some cases you may need to persist a local variable between two states. Take this for example, which is an attack providing a 10-frame window to input another command before returning to Idle:

```
[Statedef 200]
type = S
movetype = A
local = attackType

[State ]
type = VarSet
trigger1 = Command = "a"
attackType = int(1)

[State ]
type = VarSet
trigger1 = Command = "b"
attackType = int(2)

[State ]
type = ChangeState
trigger1 = attackType != 0
value = 201

[State ]
type = ChangeState
trigger1 = Time > 10
value = 0
```

- The variable attackType is specific to this attack, so it makes sense to declare it as local. However the followup state 201 will not have access to this variable.
- Pass the local through in the ChangeState. MTL will identify this and ensure the slot used by the local is not overwritten in the next state.

```
[State ]
type = ChangeState
trigger1 = attackType != 0
value = 201
persist = attackType
```

- You must also specify attackType as a local in the followup state (201). The compiler will emit an error if a variable is persisted but not redeclared as local.

- MTL also permits setting default values for locals on state entry:

```
[Statedef 200]
type = S
movetype = A
local = attackType := int(0)
```

MTL will ensure the variable `attackType` is initialized to 0 at Time=0. If the state is recursive or re-entered, the variable WILL be re-initialized.

## 7. Named Variables

- MTL allows the use of variable names instead of `var` and `fvar` names. This aids in code readability.
- MTL will reserve variable space for all global variables, as well as extra variable space for locals per statedef.
- If the input file uses legacy variable references (`var` and `fvar`), the compiler must be informed the ranges of variable numbers which are in use. If these are not provided, the compiler will produce an error.

- Because the type of named variables can't be inferred, all named variable assignments must be constructed with the variable type:

```
[State ]
type = VarSet
trigger1 = 1
VARIABLE NAME = int(VARIABLE VALUE)

[State ]
type = Null
trigger1 = VARIABLE_NAME := byte(8)
```

- When using legacy variable references, the type can be omitted.
- If the type of a variable changes unexpectedly, the compiler will produce an error.

## 8. Animation, Sprite, Sound References

## 9. Constant Triggers

- MTL allows specification of constant triggers with values that resolve at compile-time. 

## 10. Builtin Constant Triggers

MTL provides a set of built-in constant triggers which are resolved at compile-time. They can be used to inspect the state of the compiler and retrieve information from the type system. As these are const triggers, they are resolved into constant values during translation.

### cast(o: any, T: Type): T

Converts the representation of `o` in the compiler to a value of type `T`. Translation throws an error if `o` does not have the same size as `T`. This is mostly used to convert between similar types, e.g. `byte` -> `char`.

### etoi(e: any): int

Converts an enumeration value `e` to its integer representation. The compiler does this conversion automatically during translation, but it can be done explicitly here as well.

If `e` is not a constant (is stored in a variable), the compiler must emit commands to convert this to integer representation.

If `e` is not an enumeration value, an error is emitted.

### itoe(i: int, e: Enum): int

Converts an integer `i` to the corresponding value in the enum `e`. This is equivalent to `cast(i, e)`.

### isset(o: any, f: Flag): bool

Checks whether or not the flag constant `f` is set on the value `o`. `o` should be a flag value.

### sizeof(t: Type): int

Returns the size (in bytes) of type `t`. For structures, the size is the total size occupied by an instance of that type in variable memory.

### sizeof(o: any): int

Equivalent to `sizeof(typeof(o))`.

### typeof(o: any): Type

Returns the type definition for a given object. Keep in mind that a `Type` will decay into an `int` if it is used anywhere other than a translation-time context.

### typeindex(t: Type): int

Returns the type index for a given type. This can be used to compare types at runtime. Type aliases will have equivalent `typeindex` values.

### typeindex(o: any): int

Equivalent to `typeindex(typeof(o))`.

### typeindexalias(t: Type): int

Returns the alias type index for a given type. This is equivalent to `typeindex(t)`, except when `t` is an alias type, in which case this returns the alias type index.