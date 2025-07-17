## Translation Process

Translation happens in several phases. This document goes into implementation details on how an input file should be converted into valid CNS.

### 1. INI Processing

Parse the input file as a generic INI file. Identify syntactical issues here related to section headers, comments, unterminated strings, etc. At this point no type checking or grouping is necessary.

### 2. Target Processing

Parse the INI section list as a target file. `Target file` here means as either a CNS file or an MTL file, depending on the file extension. 

When parsing in CNS mode, INI sections should be grouped into State Definition groups with State Controller child groups.

When parsing in MTL mode, INI sections should be grouped into State Definition groups with State Controller child groups. In addition, MTL-specific Define and Include groups should be grouped:

- `Define Type` may not contain children, and should be followed by a new group.
- `Define Template` may contain zero or one `Define Parameters` child, and one or more `State` children.
- `Define Trigger` may contain zero or one `Define Parameters` child, and should be followed by a new group.
- `Define Structure` must contain exactly one `Define Members` child.
- `Include` may not contain children, and should be followed by a new group.

#### 2.1. Trigger Parsing

Parse trigger expressions (in state controllers under statedef or define template, as well as the `value` prop in define trigger) to ASTs here for later processing. Emit syntax issues as errors.

When parsing in CNS mode, translation can skip to step # from here (as no MTL structures will exist for translation).

### 3. Include Processing

Identify any `Include` sections. Identify the source file for inclusion and run translation steps 1, 2, and 3 against it, retrieving its output state.

Search for inclusions in the following paths, in order:

- Home directory of project
- Directory of current file
- Directory of mtlcc.py
- Absolute path

Since included files also run inclusions, cycle detection needs to be applied. If a cycle is detected, translation should terminate with an error.

If the `Include` section specifies imported names, strip the output state from inclusion down to only the required names. Any imported names which do not exist in the target should emit a warning.

If the `Include` section specifies a namespace, prepend the namespace to all included templates and triggers.

Insert the output chunks into the head of the source file context.

### 4. Type Procesing

Identify any `Define Type` sections. For each type definition, register the definition in the translation context.

Process types in a top-down fashion, identifying any missing types and emitting errors for them. The translator must identify at this point the size of all defined types.

If a type is defined more than once, the translator must emit an error.

For union types, the translator must verify the size of the union components aligns, and emit an error otherwise.

After all types have been processed, structures must also be processed into types. The size of a structure must be set to the sum of the sizes of the members.

### 5. Trigger Processing

Identify any `Define Trigger` sections. For each trigger definition, register the definition in the translation context.

The trigger must be uniquely identifiable by name and input parameters. Two triggers may use the same name, as long as input parameters differ.

The trigger name also must be distinct from type names.

For each parameter defined by the trigger (in its `Define Parameters` section), the type of the parameter must be known.

Triggers are not permitted to reference either local or global variables; the intended use is for any variables required by the trigger to be passed as parameters.
At this stage of translation variable names and scopes are not known anyway, so any identifier which is not recognized as a parameter should be rejected.

The trigger expression should be type-checked at this point and the resolved type of the trigger should be checked against the type stated by the developer.

### 6. Template Processing

Identify any `Define Template` sections. For each template definition, register the definition in the translation context.

The template name must be globally unique, and cannot overlap with any state controller name.

For each local variable defined in the template, the variable should be renamed to something globally unique (to avoid risk of conflicts during template inclusion). All uses of the variable in the template's controllers must also be updated.

A table identifying all local variables used by the template should be stored for reference.

All state controller parameters should be checked to ensure only local and parameter variables are used. The use of global variables within templates is not permitted.

### 7. Template Replacement

For each statedef defined by the project, iterate the state controllers to identify uses of templates.

Templates are permitted to make calls to other templates, so this process must be repeated until all templates are resolved. It is permitted for the compiler to apply a maximum iteration count for template resolution.

Wherever a template is referenced, identify the expressions which populate the template's parameters. Copy the template controllers into the current statedef, making replacements for the template's parameters with the provided expressions.

If the template declares locals, add new local definitions to the calling statedef.

The triggers applied to the template call must be joined together, converted into a `triggerall` statement, and applied to all included state controllers.

### 8. State Count Check

After template replacement, do a quick check to confirm all statedefs are below 512 states. This is a sanity check to ensure the character does not exceed limits imposed by MUGEN.