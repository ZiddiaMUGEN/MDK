This document outlines the CNS syntax extensions provided by tMUGEN and how the compiler should handle each construct.

## Compiler State

tMUGEN compilers may store some information in player or helper variables

### Time

In certain use cases (e.g. loops), the standard Time trigger provided by CNS cannot be relied on.
tMUGEN instead tracks time using a variable. Both players and Helpers will use the same variable to ensure consistency.
At any state change, the variable must be reset to 0:

```
triggerall = var(x) := 0 || 1 ;; tMUGEN: Time reset
```

### Jump

In certain use cases (e.g. gotos), the character may need to store information about what code to jump to within a statedef.
tMUGEN will store this information in a variable.

## New Controllers

tMUGEN defines some additional controller types.

### Custom Controllers and Import

tMUGEN provides an implementation of custom controllers which can be imported.
Imports should be evaluated early. Once a controller is imported, it should be available globally.
Imports should also be permitted at global scope (outside of a statedef).

#### Import Construct Syntax
Construct type = `Import`

Parameters:
- triggers are not valid for this construct.
- `source` - the file or module the imported controller resides in.
- `name` - the controller to be imported.

#### Custom Controller Syntax

When imported for use, it is used the same way as any builtin controller, and the imported module should be referenced for parameters.

For an example of how to define a custom controller, see below.

#### Usage

In a separate file `example.tm`, define a custom controller:

```
;; defines the name of the controller.
[ControllerDef]
name = UnifiedHelper

;; defines an input parameter to the controller.
[Parameter]
name = id
type = int
required = yes ;; defaults to `no`. compiler will show an error if a required parameter is omitted.

;; each `State` block defines the code for the controller.
;; you can choose to not define triggers here. any triggers defined here must be collapsed+merged with the caller's triggers anyway.
[State x]
type = Helper
id = id ;; use of parameter
helpertype = player
```

In your main file, import and use it:

```
[Import]
source = example.tm
name = UnifiedHelper

[Statedef 0]
[State 0]
type = UnifiedHelper
trigger1 = !NumHelper(1)
id = 1
```

### Goto

tMUGEN provides a Goto construct, which can be used to jump to a specific label in a statedef.
The Goto construct is state-local, which means a Goto can only jump to a Label from the same statedef.

#### Label Construct Syntax
Construct type = `Label`

Parameters:
- triggers are not valid for this construct.
- `name` - a unique name for the label, which can be referenced by a Goto.

#### Goto Construct Syntax
Construct type = `Goto`

Parameters:
- triggers are valid for this construct.
- `target` - the name of a Label construct to jump to.

#### Usage

For example, the below is effectively a loop using Goto and Label which will spawn 10 Helpers:

```
[State 0]
type = Label
name = MyTarget

[State 0]
type = Helper
trigger1 = var(1) < 10
id = 1000 + var(1)

[State 0]
type = Goto
trigger1 = var(1) < 10
trigger1 = (var(1) := var(1) + 1) || 1
target = Label
```

#### Compilation

The compiler should implement Label/Goto using the Jump variable from the compiler state. See below, where `x` is the Jump variable, and should have been reset on entry:

```
[Statedef 0]
[State 0]
type = Helper
triggerall = var(x) = 0
trigger1 = var(1) < 10
id = 1000 + var(1)

[State 0]
type = ChangeState
trigger1 = var(1) < 10
trigger1 = (var(1) := var(1) + 1) || 1
value = 0

[State 0]
type = Null
trigger1 = var(x) := 1

...continue on, below controllers will check var(x) = 1
```

### Loops

Not implemented in first effort, but should be reasonably close to Goto/Label implementation so should return to this. TODO