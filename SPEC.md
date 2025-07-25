# MDK Standard

This document describes a specification of features which extend and enhance the MUGEN character development experience. An implementation of this specification will take, as input, source code in a source language specified by the implementation; and produce, as output, a CNS file which can be ran as part of a character's code by MUGEN.

## Table of Contents

1. CNS Compatibility
    1a. Permitted Loss of Functionality
2. Type System
    2a. Built-in Types
    2b. Tuples, Optionals, and Repeated Types
    2c. Custom Types
    2d. Type Conversion Rules
3. Template Definitions
4. Trigger Definitions
    4a. Operator Triggers
5. Named State Definitions
6. Named Variables
    6a. Variable Scope and Initialization
7. Character Resource References
8. State Controller Repetition (Loops)
9. State Definition Scope
10. Constant Triggers
    10a. Built-in Constant Triggers

## 1. CNS Compatibility

Implementations must maintain compatibility with features already provided by the CNS language. The CNS specifications are provided by Elecbyte under https://www.elecbyte.com/mugendocs/cns.html (among other pieces of documentation, such as the State Controller and Trigger references).

Users must be able to use the following features as part of any implementation. This is not an exhaustive list; assume anything in the Elecbyte docs which are not listed here should also be supported; however this is a list of 'core' features which should be considered first.

- Create State Definitions, State Controllers within State Definitions, Triggers within State Controllers
    - For state definition properties: Properties must be type-checked at compile time.
    - For triggers: Implementations do not need to support trigger groups or `triggerall` explicitly. If the implementation can reduce its conditionals to one or more `trigger1` statements, it is permitted to do so.
- Persistent and IgnoreHitPause statements
    - Implementations should take care to provide a feature for `persistent`. Implementations should not delegate `persistent` to the user by requiring it to be built in to triggers instead.
- Trigger Redirection
- Arithmetic Precedence
    - Refer to the documentation under https://www.elecbyte.com/mugendocs/cns.html#arithmetic-operators. If the source language does not provide the same operator precedence as CNS, the implementation is permitted to use the precedence of the source language, provided the difference is well-documented.
- Multi-valued Triggers
    - as an example, refer to the `priority` parameter on the `HitDef` state controller, which takes as input a tuple `hit_prior, hit_type`. The implementation must be able to represent these multi-valued or tuple trigger types.
- Optional and Repeated Trigger Components
    - as an example, refer to the `attr` parameter on the `HitDef` state controller. In the documentation, this takes a single input of type `string`, but that `string` can be decomposed into a tuple with variable length, comprised of `hit_type, hit_attr, hit_attr, ...`. The implementation must be able to accept multiple `hit_attr` arguments in this case and in similar cases. It is not permitted to treat this case as a simple `string` as this results in loss of type accuracy.

### 1a. Permitted Loss of Functionality

The specification allows for the implementation to avoid implementing a small number of CNS features. These are features which can conflict with the functionality provided by the MDK extensions.

- `var`, `fvar`, `sysvar`, and `sysfvar` triggers can be left unimplemented, though it is recommended to still provide bare functionality for compatibility.

    These triggers conflict with the MDK functionality of named variables. MDK implementations need to be able to assign variable indices to each named variable, which can be difficult or impossible to do if the range of variables accessed by index is not known. For example, consider the below CNS statement:

    ```
    var(var(1) + 5) := 5
    ```

    In this example, we know that `var(1)` implies index `1` is already in use and cannot be reserved for use by the implementation. But we do not know the range of variables which `var(var(1) + 5)` can represent. Therefore, the implementation cannot safely assign variables without the potential for overlap.

    It is recommended to implement these triggers, and make a best-effort attempt to identify indices which are in use. The implementation is permitted to partially implement this feature and throw warnings or errors if it cannot identify the full range of indices in use.

## 2. Type System

The CNS language provides only 2 fundamental variable types (`int` and `float`) which are implicitly convertible with one another, in both directions. CNS also specifies a handful of other types (strings and enumeration/flag types) which cannot be stored in variables.

MDK defines several additional types, as well as the option to create user-defined types. In addition, implementations are required to perform thorough type checking.

For implementations where type-checking is provided as part of the source language, it is encouraged to make use of the source language's type system. The implementation may be required to provide additional functions or features to meet the type conversion requirements of the spec.

### 2a. Built-in Types

Implementations must provide each of the following types. More details on the representation of each type in the resulting CNS and how values may be stored inside variables of larger size is provided in section `6`.

- `int`: integer, 32 bits
- `float`: floating point, 32 bits
- `short`: integer, 16 bits
- `byte`: integer, 8 bits
- `char`: integer, 8 bits: stores only ASCII character codes.
- `bool`: integer, 1 bits

Implementations are also required to implement the below extended types in order to provide CNS compatibility:

- `numeric`: union[int, float]
- TODO: list out the enums/flags we support as part of MTL here.

Implementations are not required to provide the below types, but it is strongly encouraged to provide them in some way. In source languages which support type introspection (e.g. using the `type` keyword in Python) it is permitted to implement these types using source language features.

- `type`: Represents an arbitrary type known to the implementation.

### 2b. Tuples, Optionals, and Repeated Types

The type system in use must be able to represent several type extensions which are not defined in the CNS standard, but are regardless in use within CNS. This section will define each of these type extensions and describe how implementations must support them.

#### Tuples

There are many state controller parameters which accept multi-values or tuples as inputs. For an immediate example look at any state controller parameter which accepts a color: `palbright = add_r, add_g, add_b` it is immediately clear that the parameter accepts a 3-tuple.

Within CNS, tuple members are permitted to have different types. For example, the `ForceFeedback` controller accepts 2 parameters `freq` and `ampl` which are 4-tuples, of which 1 member is `int`, and the others are `float`.

Implementations must be capable of representing arbitrary `n`-tuples of mixed types. If the implementation relies on its source language's type checking system to provide type checks, it must also ensure the representation of each field accepting a tuple is set correctly.

#### Optionals

There are certain state controller parameters which accept a tuple, but where one or more of the tuple's members are optional. For example, refer to the `priority` parameter for the `HitDef` state controller, which is defined as a `tuple[int, string]`. However, the CNS state controller reference specifies that the second member can be omitted, in which case a default value of `Hit` will be used.

Implementations must be able to support optional tuple members within its type-checking system. If the implementation's source language supports default values for missing tuple members, then the implementation is permitted to make use of that functionality, provided it is well-documented. Note that though there is no difference between e.g. `priority = 4` and `priority = 4, Hit`, it is still an addition to the end user's code which they should be made aware of.

#### Repetition

There are a very small number of state controller parameters which can accept an arbitrary number of tuple members. For example, refer to the `NotHitBy` state controller's `value` parameter, which accepts a hit string. Loosely, the hit string can be defined as `HitType, HitAttr`, where `HitType` is one or more of `S,C,A`, and `HitAttr` is one of more of `N,S,H,A,T,P`. However, each `HitAttr` can only specify one attribute pair (for example, `NA` or `ST`). In order to pass multiple attributes to the controller, additional pairs must be specified (e.g. `SCA,AA,AT,AP`). In these specific cases, the type of the hit string is really `HitType, HitAttr, ...` where `...` represents an arbitrary number of repetitions of `HitAttr`.

Implementations are already required to be able to represent arbitrary `n`-tuples in their type system, but must also be able to support tuples of variable size.

### 2c. Custom Types

The implementation must provide a way for users to define custom types. User-defined types will fall into one of 4 categories. It is permitted for the implementation to use the source language's type system for this purpose, so long as the implementation can constrain it enough to ensure the types fit into one of the categories.

- `alias`: Provides a way to define type aliases. This is mostly for convenience and readability. An alias type will always be mapped to a single source type, and the implementation is expected to treat the alias type as if it were the source type (it is permitted for the implementation to simply collapse aliases into their ultimate source types during processing and pretend aliases do not exist).
- `union`: Provides a way to define unions of multiple types. It is permitted to classify trigger and template parameters as taking `union` types as input, but it is not permitted to create a variable from a `union` type. For example, the built-in union type `numeric` (`union[int, float]`) can be used as an input type for several built-in CNS triggers, but it is not permitted to create a variable of type `numeric`. Implementations are expected to identify the concrete type in use for each location where a union type parameter is populated.
- `enum`: Provides a way to define integer-backed enumerations. The end user should be able to define the name of the enumeration and a list of members; then they can reference the members of that enumeration in triggers and as parameters. Implementations are required to convert enum types to their integer representation when emitting them into CNS, as the CNS format does not permit use of arbitrary strings.
- `flag`: Similar to the `enum` type, but allows specifying multiple enumeration constants at the same time. Implementations are required to assign a power-of-two to each flag constant (to assign a single bit from the backing integer to each constant). Implementations must then convert the flag type to the combination of the integer representation of each flag constant assigned.
- `struct`: A collection of several variables into a single structure. Implementations must be able to calculate the size of a `struct` type in order to assign it to variables. In addition, implementations must provide a way for the user to set and access the individual members of a structure.

### 2d. Type Conversion Rules

Implementations are permitted to provide implicit type conversions between specific types. Implementations are also required to provide built-in triggers which convert expressions between types (see section `10a` and the `cast` trigger in particular).

For the builtin types:
- `int` is implicitly convertible to `float`.
- `float` cannot be implicitly converted to `int` as it results in loss of precision.
- smaller builtin types can implicitly convert to wider ones (`bool`->`byte`->`short`->`int`)
- `char` is implicitly convertible to `byte`, but the reverse is not true, as `byte` may contain values which are not defined in ASCII.

For user-defined types:
- `alias` types are resolved to their source type.
- `enum` can be converted to `int` via builtin functions, and vice versa.
- `flag` can be converted to `int` via builtin functions, and vice versa.
- single `flag` values can also be converted to `bool` via builtin functions.

## 3. Template Definitions

Implementations must provide a way for users to create reusable, modular pieces of code, which are described as 'templates' in this document. The implementation must allow templates to receive parameters. Users can then call their templates at any point within any of their state definitions.

The parameters to the template are substituted with the values provided at the call site of the template. Then, the contents of the template are inserted into the source state definition, at the location of the call.

Templates are also permitted to make use of local variables (see section `6a`). Implementations are permitted to 'hoist' the local variables defined in a called template up to the root of the state definition which makes use of the template. However, for implementations which support granular scopes (as defined in `6a`), it is encouraged to create a smaller scope for the template call to reduce the overall variable usage.

For implementations whose source language supports functions and function calls, it is permitted to treat functions as 'templates' (provided the implementation can differentiate between normal/template functions and functions whichs should be assigned to state definitions).

## 4. Trigger Definitions

Implementations must provide a way to create user-defined triggers. A user-defined trigger is just a named function which accepts zero or more parameters and produces a single output. The types of the inputs and output for the trigger must be well-known to the implementation.

Implementations must also provide support for trigger overloading. Trigger overloading allows the same trigger to be used with the same name but with different input types. This enables users to define triggers which can accept various input types without relying on precarious unions such as `numeric`.

### 4a. Operator Triggers

Implementations must provide a way to define the behaviour of operators. For example, if a user has defined a `struct` type with an `int` member and a `float` member, they should be able to define the behaviour of the `+` (addition) operator between two of these structs (or between the struct and an int, or the struct and a float, etc).

## 5. Named State Definitions

Implementations must provide a way to set the name of a state definition. The CNS syntax uses integer IDs for state definitions, but string names can make it easier to identify the purpose of a state definition.

The implementation must also provide a way to explicitly specify the ID of a state definition, as some state IDs are used for built-in states (e.g. 20 for walk, 11 for crouch) and some IDs are used for community standards.

The implementation must be able to identify the full list of integer IDs in use, and then assign unused IDs to each named state definition.

When the user is referencing character resources as parameters (see section `7`), the implementation must be able to identify this and should decompose state definition names into their integer IDs when converting the input to CNS.

## 6. Named Variables

Implementations must provide a way to create named variables. Similar to named state definitions, it is easier to identify the purpose of a variable if it is given a name.

As per section `1a`, it is permitted for the implementation to skip implementation of ID-based variables. If the implementation chooses to provide ID-based variables to the user, it must also identify which IDs are in use before assigning IDs to named variables (or emit a warning or error if it cannot determine the IDs in use).

When a named variable is declared its type must also be made explicit to the implementation. Attempts to assign a value of a different type to a named variable should result in a type check failure.

Implementations must guarantee that integer-based types are assigned to `var` indices, and float-based types are assigned to `fvar` indices. The implementation must also specify a way for a user to create system variables (`sysvar` and `sysfvar`).

### 6a. Variable Scope and Initialization

Implementations must provide a way to specify the scope of named variables. The minimum which an implementation must provide is a global and a local scope: globally-scoped variables are available to all state definitions, while locally-scoped variables are available only to the state definition where they are declared.

When the implementation is assigning indexes to named variables, it must first determine the full set of global variables which have been defined, as this defines the size of variables which need to be reserved at all times. Available variable indices should be assigned immediately to globals. Then afterwards, the implementation can determine the size of local variables required for each individual state definition, and assign those indices on a state-by-state basis.

Implementations must also specify a way to initialize variables on entry into a state (i.e. when `Time = 0`). Implementations must initialize all local variables on entry to the state which defines them (either to the specified initial value, or to an initial value of `0`). Implementations must also provide a way for users to specify an alternative initialization trigger (for use cases such as throw escaping where `Time` will likely always be set to `0`).

It is encouraged, but not required, to also provide the following scope-related features:

- **Persistence**: provide a way to feed local variables in state `A` through to the local variables in state `B` during a state change.
- **Granular scopes**: provide a way to create sub-scopes within the local scope, which allocate and free variable indices as part of the scope. This would permit, as an example, allocation of `n` indices the first time a template is invoked in a state definition, and then reuse of the same `n` indices the next time the template is invoked.

## 7. Character Resource References

Implementations must provide a way to reference character resources. In particular, the following resources must be referenceable:

- `anim`: Animations must be referenceable from the character's code. It is encouraged for the implementation to create a specific `anim` type which decays to `int`, and to verify that the animation exists in the character's AIR file wherever this type is used.
- `sound`: Sounds must be referenceable from the character's code. It is encouraged for the implementation to create a specific `sound` type which decays to `int,int`, and to verify that the sound exists in the character's SND file wherever this type is used.

It is also recommended, but not required, for implementations to provide a way to assign names to animations and sounds. This would then allow animations and sounds to be referenced by user-friendly names within their code.

## 8. State Controller Repetition (Loops)

Implementations must provide a way to expose compile-time repetition to the user. Note that this repetition is **compile-time**, which means the implementation does not need to provide a way to run arbitrary-count loops as part of the character's code.

Repetitions should accept a constant value, known at compile time, for the number of iterations. The implementation will repeat the group of controllers specified as part of the repetition however many times are specified. In addition, the implementation must provide a variable for the index of repetition. As a pseudo-code example, the below:

```
repeat 3:
    Helper(1000 + index)
```

Would be expanded to:

```
Helper(1000 + 0)
Helper(1000 + 1)
Helper(1000 + 2)
```

If the number of iterations is not a constant expression, the implementation should not permit the repetition. (See section `10` for information on constant expressions).

## 9. State Definition Scope

Implementations should provide a way to specify the scope of a state definition. The scope of a state definition specifies which actors (players, enemies, or helpers) are expected to execute that state. For example, a state definition with a scope of `enemy` is expected to be used only as the target state for a throw or a `TargetState` controller.

The valid scopes defined by this specification are:
- `player` - for states which the root can enter.
- `enemy` - for states which the enemy is sent to during a custom state.
- `helper` - for states which can be entered by helpers, but not the root.
- `shared` - for states which are usable by both the root and its helpers.

Implementations must attempt to validate that these scopes are effective. For example, implementations must detect if it is possible for a player to move via ChangeState from a `player`-scoped state to an `enemy`-scoped state and provide warnings or errors.

Because the hurt states from the CNS common state file can be reached by Helpers if they get hit, these should all be specified as `shared` states which can be entered by either players or helpers.

Implementations should allow `helper`-scoped states to specify the exact helper index which will be using the state, for further validation.

It is encouraged for implementations to provide an option to disable the `shared` state definition scope, as this helps strengthen the scoping and eliminate unexpected errors. It is also encouraged for implementations to provide an option to enforce scopes at runtime - for example, by adding a block like this at the start of every `helper` state:

```
[State ]
type = SelfState
trigger1 = !IsHelper(xxx)
value = 0
ctrl = 1
```

## 10. Constant Triggers

TBD.

### 10a. Built-in Constant Triggers

The implementation must provide all of the following triggers as constant expressions which are resolved at compile time. The implementation may also provide any number of additional triggers which are specific to their own implementation.

#### cast(v: any, t: type)

Takes an expression `v` of any type and converts it to the type `t`. This is an escape hatch in case of typing issues.