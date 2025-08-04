# mtldbg

The MTL tooling comes equipped with a CNS/MTL debugger, `mtldbg.py`. This tool is able to load debugging information from an external debugging database and launch MUGEN with attached debugging.

This document outlines usage of `mtldbg.py` and the format of the `mdbg` external debugging database.

## Usage

Run `mtldbg.py` with Python.

Pass `-c <character def file>` to invoke `mtlcc` and compile a character, then immediately launch the debugger for the compiled character.

Pass `-d <debugging database file>` to launch the debugger with information from the provided database.

Pass `-m <mugen.exe>` to specify the path to the MUGEN installation you will use for debugging.

Pass `-p <character path>` to specify the P2 character to use with debugging. By default this will use KFM.

Pass `-a <on|off>` to enable or disable AI in the launched MUGEN process.

## Debugging Database

The debugging database stores debugging information.

All strings are length-encoded, 2 bytes encode the length and go before the string.

Trigger trees are stored in the following format, which is arbitrary-length:

- 1 byte: node type
- string: node operator
- 1 byte: child count
- for each child:
    - store an additional tree

### Header

A string stores the version of `mtlcc` used to compile the character. The maximum length of this string is 14 characters (+2 to encode the length).

A 4-byte integer is used to store the version of the debugging database format used for this database.

An additional 60 bytes of space are reserved for more header information in the future.

### Body

#### 1. Strings Table

Stores every string used in the debugging database, which allows for strings to be reused where needed.

4 bytes are written to indicate the number of strings in the database.

For each string, the first 2 bytes encode the string length; then the string is encoded directly.

#### 2. Type Definitions

Stores every type definition (including builtins).

4 bytes are written to indicate the number of type definitions in the database.

For each type definition, store the following information:

- 4 bytes: name (index into string table)
- 1 byte: category
- 2 bytes: member count
    - for each member:
    - 4 bytes: index into string or type table for member (determined by category)
    - 4 bytes: NULL unless category is structure; index into string table for member name
- 4 bytes: index into string table for filename
- 4 bytes: line number for definition

#### 3. Trigger Definitions

4 bytes are written to indicate the number of trigger definitions in the database.

For each trigger definition, store the following information:

- 4 bytes: name (index into string table)
- 1 byte: category
- 4 bytes: return type (index into type table)
- 2 bytes: parameter count
    - for each parameter:
    - 4 bytes: index into type table for parameter type
    - 4 bytes: index into string table for parameter name
- ? bytes: expression tree - OMITTED FOR NOW
- 4 bytes: index into string table for filename
- 4 bytes: line number for definition

#### 4. Template Definitions

4 bytes are written to indicate the number of template definitions in the database.

For each template definition, store the following information:

- 4 bytes: name (index into string table)
- 1 byte: category
- 2 bytes: parameter count
    - for each parameter:
    - 1 byte: specifier count
    - for each specifier:
        - 4 bytes: index into type table for specifier type
    - 4 bytes: index into string table for parameter name
- 2 bytes: local count
    - for each local:
    - 4 bytes: index into type table for local type
    - 4 bytes: index into string table for local name
- TODO: template state controllers
- 4 bytes: index into string table for filename
- 4 bytes: line number for definition

#### 5. Global Variable Table

4 bytes are written to indicate the number of global variable declarations in the database.

For each variable declaration, store the following information:

- 4 bytes: name (index into string table)
- 4 bytes: type (index into type table)
- 1 byte: scope_type
- 4 bytes: scope_target (or -1 for none)
- 2 bytes: allocation count
    - for each allocation:
    - 1 byte: target variable
    - 1 byte: target offset

#### 6. State Definitions

4 bytes are written to indicate the number of statedefs in the database.

For each statedef, store the following information:

- 4 bytes: name (index into string table)
- 4 bytes: ID
- 1 byte: scope_type
- 4 bytes: scope_target (or -1 for none)
- 4 bytes: index into string table for filename
- 4 bytes: line number for definition
- ? bytes: Local Variable Table
- ? bytes: State Controller Locations

##### 6a. Local Variable Table

A local variable table is nested in each state definition. The format is identical to the global variable table, but scopes are omitted (as the local scope matches the statedef scope).

- 2 bytes: local count
    - for each local:
    - 4 bytes: name (index into string table)
    - 4 bytes: type (index into type table)
    - 2 bytes: allocation count
        - for each allocation:
        - 1 byte: target variable
        - 1 byte: target offset

##### 6b. State Controller Locations

For each controller in the statedef, data is produced for the location of the controller.

This is for each controller post-expansion (so e.g. if a template is called containing 3 controllers, the location information encoded will be for the expanded representation, 3 entries).

- 2 bytes: controller count
    - for each controller:
    - 4 bytes: index into string table for filename
    - 4 bytes: line number for definition