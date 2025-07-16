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

Since included files also run inclusions, cycle detection needs to be applied. If a cycle is detected, translation should terminate with an error.

If the `Include` section specifies imported names, strip the output state from inclusion down to only the required names.

If the `Include` section specifies a namespace, prepend the namespace to all included templates and triggers.

Insert the output chunks into the head of the source file context.

### 4. Type Procesing

Identify any `Define Type` sections. For each type definition, register the definition in the translation context.

Process types in a top-down fashion, identifying any missing types.