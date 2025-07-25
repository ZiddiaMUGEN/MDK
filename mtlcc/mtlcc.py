import argparse
import os
import traceback
import re
import copy
from typing import List

from mtl.parsers import ini, trigger
from mtl.shared import *
from mtl.error import TranslationError
from mtl.utils import *
from mtl import builtins

def parseTarget(sections: List[INISection], mode: TranslationMode, ctx: LoadContext):
    ## group sections into states, templates, triggers, types, includes, etc
    index = 0
    while index < len(sections):
        section = sections[index]
        if section.name.lower().startswith("statedef "):
            statedef = StateDefinitionSection(section.name[9:], section.properties, section.location)
            ctx.state_definitions.append(statedef)

            while index + 1 < len(sections) and sections[index + 1].name.lower().startswith("state "):
                properties: List[StateControllerProperty] = []
                for property in sections[index + 1].properties:
                    properties.append(StateControllerProperty(property.key, trigger.parseTrigger(property.value, property.location), property.location))
                statedef.states.append(StateControllerSection(properties, sections[index + 1].location))
                index += 1
        elif section.name.lower().startswith("include"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Include sections.", section.location)
            ctx.includes.append(section)
        elif section.name.lower().startswith("define type"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.location)
            
            if (name := find(section.properties, lambda k: k.key.lower() == "name")) == None:
                raise TranslationError("Define Type section must provide a name property.", section.location)
        
            if (type := find(section.properties, lambda k: k.key.lower() == "type")) == None:
                raise TranslationError("Define Type section must provide a type property.", section.location)

            ctx.type_definitions.append(TypeDefinitionSection(name.value, type.value, section.properties, section.location))
        elif section.name.lower().startswith("define template"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.location)
            
            if (prop := find(section.properties, lambda k: k.key.lower() == "name")) == None:
                raise TranslationError("Define Template section must provide a name property.", section.location)
            
            template = TemplateSection(prop.value, section.location)
            ctx.templates.append(template)

            ## read any local definitions from the define template block
            locals: List[INIProperty] = []
            for prop in section.properties:
                if prop.key == "local":
                    locals.append(prop)
            template.locals = locals

            while index + 1 < len(sections):
                if sections[index + 1].name.lower().startswith("state "):
                    properties: List[StateControllerProperty] = []
                    for property in sections[index + 1].properties:
                        properties.append(StateControllerProperty(property.key, trigger.parseTrigger(property.value, property.location), property.location))
                    template.states.append(StateControllerSection(properties, sections[index + 1].location))
                elif sections[index + 1].name.lower().startswith("define parameters"):
                    if template.params != None:
                        raise TranslationError("A Define Template section may only contain 1 Define Parameters subsection.", sections[index + 1].location)
                    else:
                        template.params = sections[index + 1]
                else:
                    break
                index += 1
        elif section.name.lower().startswith("define trigger"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.location)
            
            if (name := find(section.properties, lambda k: k.key.lower() == "name")) == None:
                raise TranslationError("Define Trigger section must provide a name property.", section.location)
            if (type := find(section.properties, lambda k: k.key.lower() == "type")) == None:
                raise TranslationError("Define Trigger section must provide a type property.", section.location)
            if (value := find(section.properties, lambda k: k.key.lower() == "value")) == None:
                raise TranslationError("Define Trigger section must provide a value property.", section.location)

            trigger_section = TriggerSection(name.value, type.value, trigger.parseTrigger(value.value, value.location), section.location)
            ctx.triggers.append(trigger_section)
            if index + 1 < len(sections) and sections[index + 1].name.lower().startswith("define parameters"):
                trigger_section.params = sections[index + 1]
                index += 1
        elif section.name.lower().startswith("define structure"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.location)

            if index + 1 >= len(sections) or not sections[index + 1].name.lower().startswith("define members"):
                raise TranslationError("A Define Structure section must be followed immediately by a Define Members section.", section.location)
            
            if (prop := find(section.properties, lambda k: k.key.lower() == "name")) == None:
                raise TranslationError("Define Structure section must provide a name property.", section.location)

            structure = StructureDefinitionSection(prop.value, sections[index + 1], section.location)
            ctx.struct_definitions.append(structure)
            index += 1
        elif section.name.lower().startswith("state "):
            # a standalone 'state' section is invalid. raise an exception
            raise TranslationError("A State section in a source file must be grouped with a parent section such as Statedef.", section.location)
        elif section.name.lower().startswith("define parameters"):
            # a standalone 'state' section is invalid. raise an exception
            raise TranslationError("A Define Parameters section in a source file must be grouped with a parent section such as Define Template.", section.location)
        elif section.name.lower().startswith("define members"):
            # a standalone 'state' section is invalid. raise an exception
            raise TranslationError("A Define Members section in a source file must be grouped with a parent Define Structure section.", section.location)
        else:
            raise TranslationError(f"Section with name {section.name} was not recognized by the parser.", section.location)
        index += 1

def processIncludes(cycle: List[str], ctx: LoadContext):
    # although CNS mode does not support Include sections, we explicitly block parsing them in parseTarget, and we still want to include libmtl.inc for all files.
    # so we permit includes through here.
    for include in ctx.includes:
        if (source := find(include.properties, lambda k: k.key.lower() == "source")) == None:
            raise TranslationError("Include block must define a `source` property indicating the file to be included.", include.location)
        
        ## per the standard, we search 3 locations for the source file:
        ## - working directory
        ## - directory of the file performing the inclusion
        ## - directory of this file
        ## - absolute path
        search = [f"{os.getcwd()}/{source.value}", f"{os.path.dirname(os.path.realpath(include.location.filename))}/{source.value}", f"{os.path.dirname(os.path.realpath(__file__))}/{source.value}", f"{os.path.realpath(source.value)}"]
        location: Optional[str] = None
        for path in search:
            if os.path.exists(path):
                location = path
                break
        if location == None:
            raise TranslationError(f"Could not find the source file specified by {source.value} for inclusion.", source.location)
        
        ## now translate the source file
        print(f"Starting to load included file {location}")
        include_context = loadFile(location, cycle + [ctx.filename])

        ## if we specified a namespace, the imported names need to be prefixed with that namespace.
        if (namespace := find(include.properties, lambda k: k.key.lower() == "namespace")) != None:
            for template_definition in include_context.templates:
                template_definition.namespace = namespace.value
            for trigger_definition in include_context.triggers:
                trigger_definition.namespace = namespace.value
            for structure_definition in include_context.struct_definitions:
                structure_definition.namespace = namespace.value
            for type_definition in include_context.type_definitions:
                type_definition.namespace = namespace.value

        ## if there are 'import' properties present, only include names which match imported names.
        imported_names: List[str] = []
        for property in include.properties:
            if property.key.lower() == "import":
                imported_names += [property.value]
                if find(include_context.templates, lambda k: k.name == property.value) == None and \
                    find(include_context.triggers, lambda k: k.name == property.value) == None and \
                    find(include_context.type_definitions, lambda k: k.name == property.value) == None and \
                    find(include_context.struct_definitions, lambda k: k.name == property.value) == None:
                    print(f"Warning at {os.path.realpath(property.location.filename)}:{property.location.line}: Attempted to import name {property.value} from included file {include.location.filename} but no such name exists.")

        if len(imported_names) != 0:
            include_context.templates = list(filter(lambda k: k.name in imported_names, include_context.templates))
            include_context.triggers = list(filter(lambda k: k.name in imported_names, include_context.triggers))
            include_context.type_definitions = list(filter(lambda k: k.name in imported_names, include_context.type_definitions))
            include_context.struct_definitions = list(filter(lambda k: k.name in imported_names, include_context.struct_definitions))

        ## included context gets added to the HEAD of the current translation context.
        ## this ensures it is available to downstream files.
        ctx.templates = include_context.templates + ctx.templates
        ctx.triggers = include_context.triggers + ctx.triggers
        ctx.type_definitions = include_context.type_definitions + ctx.type_definitions
        ctx.struct_definitions = include_context.struct_definitions + ctx.struct_definitions

def loadFile(file: str, cycle: List[str]) -> LoadContext:
    cycle_detection = find(cycle, lambda k: os.path.realpath(file) == os.path.realpath(k))
    if cycle_detection != None:
        print("Import cycle was detected!!")
        print(f"\t-> {os.path.realpath(file)}")
        index = len(cycle) - 1
        while index >= 0:
            print(f"\t-> {os.path.realpath(cycle[index])}")
            index -= 1
        raise TranslationError("A cycle was detected during include processing.", compiler_internal())

    ctx = LoadContext(file)

    with open(file) as f:
        contents = ini.parse(f.read(), ctx.ini_context)

    ctx.mode = TranslationMode.MTL_MODE if file.endswith(".mtl") or file.endswith(".inc") else TranslationMode.CNS_MODE
    print(f"Parsing file from {file} using mode = {'MTL' if ctx.mode == TranslationMode.MTL_MODE else 'CNS'}")
    parseTarget(contents, ctx.mode, ctx)
    # create a virtual include for libmtl.inc.
    # libmtl.inc has several required types for the builtins to function.
    # only include this on the primary file.
    if len(cycle) == 0:
        ctx.includes.insert(0, INISection("Include", "", [INIProperty("source", "stdlib/libmtl.inc", compiler_internal())], compiler_internal()))
    processIncludes(cycle, ctx)

    return ctx

def findTriggerBySignature(name: str, types: List[str], ctx: TranslationContext, location: Location) -> Union[TriggerDefinition, None]:
    matches = list(filter(lambda k: k.name.lower() == name.lower(), ctx.triggers))

    # iterate each match
    for match in matches:
        is_matching = True

        ## iterate all the types from input signature and attempt to match each.
        index = 0
        while index < len(types) and index < len(match.params):
            # get typedef 1
            first_str = resolveAlias(types[index], ctx)
            first = find(ctx.types, lambda k: k.name == first_str)

            # get typedef 2
            second_str = resolveAlias(match.params[index].type.replace("...", "").replace("?", ""), ctx)
            second = find(ctx.types, lambda k: k.name == second_str)

            ## check
            if first == None:
                raise TranslationError(f"Input type {first_str} could not be found.", location)
            if second == None:
                raise TranslationError(f"Matching type {second_str} could not be found.", location)
            if typeConvertOrdered(first, second, ctx, location) == None:
                is_matching = False
                break

            ## if the target function includes repetition `...` we need to also match
            if "..." in match.params[index].type:
                while index < len(types):
                    if typeConvertOrdered(first, second, ctx, location) == None:
                        is_matching = False
                        break
                    index += 1

            index += 1

        ## if there are remaining types in the input, something went wrong
        if index < len(types): is_matching = False
        ## if there are remaining types in the target, ensure they all have `?`
        while index < len(match.params):
            if not "?" in match.params[index].type: is_matching = False
            index += 1

        if is_matching: return match

    return None

def matchesEnumValue(type: TypeDefinition, e: str, autoEnums: List[TypeDefinition], location: Location) -> bool:
    if type.category not in [TypeCategory.ENUM, TypeCategory.FLAG, TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG]: return False

    ## if the maybe-enum is unscoped, we may still match it with the automatic enum list provided.
    if "." not in e:
        for en in autoEnums:
            if matchesEnumValue(type, f"{en.name}.{e}", [], location): return True
        return False

    ## we want to split the enum into scope and value.
    value = e.split(".")[-1]
    scope = ".".join(e.split(".")[:-1])

    ## early exit if the type name doesn't match the enum we're inspecting
    if type.name != scope: return False
    ## determine if the value directly matches an enum key.
    if find(type.members, lambda k: k.lower() == value.lower()) != None: return True
    ## determine if the value matches a FLAG value. each flag value is a single character, match on each character.
    if type.category == TypeCategory.FLAG or type.category == TypeCategory.STRING_FLAG:
        for chara in value:
            if find(type.members, lambda k: k.lower() == chara.lower()) == None: raise TranslationError(f"Flag constant {chara} does not exist on enum type {type.name}", location)
        return True
    raise TranslationError(f"Enumeration constant {value} does not exist on enum type {type.name}", location)

def runTypeCheck(tree: TriggerTree, locals: List[TriggerParameter], ctx: TranslationContext, autoEnums: List[TypeDefinition] = [], isForTrigger: bool = False) -> str:
    ## for multivalue, handle single case here. true multivalue handled below.
    if tree.node == TriggerTreeNode.MULTIVALUE and len(tree.children) == 1:
        r = runTypeCheck(tree.children[0], locals, ctx, autoEnums)
        if isForTrigger and r in ["int", "short", "byte"]:
            return "bool"
        return r
    
    ## for intervals, give an error for now.
    if tree.node == TriggerTreeNode.INTERVAL_OP:
        raise TranslationError("TODO: support interval expressions correctly", tree.location)
    
    ## for atoms, early exit: just identify the type of the node.
    if tree.node == TriggerTreeNode.ATOM:
        if tryParseInt(tree.operator) != None:
            return "int"
        elif tryParseFloat(tree.operator) != None:
            return "float"
        elif tryParseBool(tree.operator) != None:
            return "bool"
        elif tryParseCint(tree.operator) != None:
            return "cint"
        elif tryParseString(tree.operator) != None:
            return "string"
        elif find(ctx.types, lambda k: k.name.lower() == tree.operator.lower()) != None:
            return "type"
        elif (local := find(locals, lambda k: k.name == tree.operator)) != None:
            return resolveAlias(local.type, ctx)
        elif (trigger := find(ctx.triggers, lambda k: k.name.lower() == tree.operator.lower())) != None:
            return resolveAlias(trigger.type, ctx)
        elif (enum := find(ctx.types, lambda k: matchesEnumValue(k, tree.operator, autoEnums, tree.location))) != None:
            ## this matches on both enums and flags.
            return resolveAlias(enum.name, ctx)
        else:
            raise TranslationError(f"Could not determine type from expression {tree.operator}.", tree.location)
        
    ## for structure access, need to determine the type of the structure being accessed.
    ## then determine the type of the field.
    if tree.node == TriggerTreeNode.STRUCT_ACCESS:
        struct_identifier = tree.operator.split(" ")[0]
        struct_access = tree.operator.split(" ")[1]
        if (local := find(locals, lambda k: k.name == struct_identifier)) != None:
            if (local_type := find(ctx.types, lambda k: k.name == local.type and k.category == TypeCategory.STRUCTURE)) != None:
                ## matches a Struct-backed trigger, fetch the type of the field
                if (local_member := find(local_type.members, lambda k: k.name.lower() == struct_access.lower())) == None:
                    raise TranslationError(f"Attempted to access an unknown member {struct_access} on struct with type {local_type.name}", tree.location)
                return local_member.type
            raise TranslationError(f"Attempted to access a structure member {struct_access} on local named {struct_identifier}, but the local is not a structure type.", tree.location)
        elif (trigger := find(ctx.triggers, lambda k: k.name.lower() == struct_identifier.lower())) != None:
            if (trigger_type := find(ctx.types, lambda k: k.name == trigger.type and k.category == TypeCategory.STRUCTURE)) != None:
                ## matches a Struct-backed trigger, fetch the type of the field
                if (trigger_member := find(trigger_type.members, lambda k: k.name.lower() == struct_access.lower())) == None:
                    raise TranslationError(f"Attempted to access an unknown member {struct_access} on struct with type {trigger_type.name}", tree.location)
                return trigger_member.type
            raise TranslationError(f"Attempted to access a structure member {struct_access} on trigger {struct_identifier}, but this trigger does not return a structure type.", tree.location)
        else:
            raise TranslationError(f"Could not determine structure type from identifier {struct_identifier}", tree.location)

    ## do a depth-first search on the tree. determine the type of each node, then apply types to each operator to determine the result type.
    child_types: List[str] = []
    if tree.node == TriggerTreeNode.MULTIVALUE:
        ## for a multivalue case, we may be passed several autoEnum values for each value.
        subindex = 0
        for child in tree.children:
            if subindex < len(autoEnums):
                nextAutoEnum = [autoEnums[subindex]]
            elif len(autoEnums) != 0:
                nextAutoEnum = [autoEnums[-1]] ## for repetition operator
            else:
                nextAutoEnum = []
            subindex += 1
            child_types.append(runTypeCheck(child, locals, ctx, nextAutoEnum, isForTrigger = isForTrigger))
    else:
        for child in tree.children:
            child_types.append(runTypeCheck(child, locals, ctx, autoEnums, isForTrigger = isForTrigger))

    ## process operators using operator functions.
    ## no need to evaluate anything at this stage, just return the stated return type of the operator.
    if tree.node == TriggerTreeNode.UNARY_OP or tree.node == TriggerTreeNode.BINARY_OP:
        if isForTrigger and tree.operator in ["&&", "||"]:
            index = 0
            while index < len(child_types):
                if child_types[index] in ["int", "short", "byte"]: child_types[index] = "bool"
                index += 1
        ## operator is stored in tree.operator, child types are above. there are builtin operator triggers provided,
        ## so determine which trigger to use.
        operator_call = findTriggerBySignature(f"operator{tree.operator}", child_types, ctx, tree.location)
        if operator_call == None:
            raise TranslationError(f"Could not find any matching overload for operator {tree.operator} with input types {', '.join(child_types)}.", tree.location)
        return resolveAlias(operator_call.type, ctx)

    ## handle explicit function calls.
    ## this is very similar to operators. find the matching trigger and use the output type provided.
    if tree.node == TriggerTreeNode.FUNCTION_CALL:
        ## special handling for the `cast` operator, because we do not have any support for generics currently.
        if tree.operator == "cast":
            if tree.children[1].node != TriggerTreeNode.ATOM:
                raise TranslationError("Second argument to cast() must be a type name, not an expression.", tree.children[1].location)
            if child_types[1] != "type":
                raise TranslationError("Second argument to cast() must be a type name, not an expression.", tree.children[1].location)
            target_type = find(ctx.types, lambda k: k.name.lower() == tree.children[1].operator.lower())
            if target_type == None:
                raise TranslationError(f"Second argument to cast() must be a valid type name, could not find a type named {tree.children[1].operator}.", tree.children[0].location)
            return resolveAlias(tree.children[1].operator, ctx)

        function_call = findTriggerBySignature(tree.operator, child_types, ctx, tree.location)
        if function_call == None:
            raise TranslationError(f"Could not find any matching overload for trigger {tree.operator} with input types {', '.join(child_types)}.", tree.location)
        return resolveAlias(function_call.type, ctx)
    
    ## handle true multivalue.
    ## just resolve it to typenames separated with commas.
    if tree.node == TriggerTreeNode.MULTIVALUE:
        child_resolved = [resolveAlias(child, ctx) for child in child_types]
        child_resolved.reverse()
        return ",".join(child_resolved)
    
    return "bottom"

def parseLocalParameter(local: INIProperty, ctx: TranslationContext) -> StateParameter:
    ## local variables are basically specified as valid trigger syntax, e.g. `myLocalName = myLocalType(defaultValueExpr)`
    ## so we parse as a trigger and make sure the syntax tree matches the expected format.
    ## there are only 2 valid formats: `name = type` and `name = type(default)`.
    tree = trigger.parseTrigger(local.value, local.location)
    if tree.node == TriggerTreeNode.MULTIVALUE: tree = tree.children[0]

    ## check the operator is correct and the first node is an atom
    if tree.node != TriggerTreeNode.BINARY_OP or tree.operator != "=":
        raise TranslationError("Local definitions must follow the format <local name> = <local type>(<optional default>).", tree.location)
    if tree.children[0].node != TriggerTreeNode.ATOM:
        raise TranslationError("Local definitions must follow the format <local name> = <local type>(<optional default>).", tree.location)
    ## the second node can be either ATOM (for type name) or FUNCTION_CALL with a single child (for default value)
    if tree.children[1].node != TriggerTreeNode.ATOM and tree.children[1].node != TriggerTreeNode.FUNCTION_CALL:
        raise TranslationError("Local definitions must follow the format <local name> = <local type>(<optional default>).", tree.location)
    if tree.children[1].node == TriggerTreeNode.FUNCTION_CALL and len(tree.children[1].children) != 1:
        raise TranslationError("Local definitions must follow the format <local name> = <local type>(<optional default>).", tree.location)
    local_type = tree.children[1].operator
    default_value = tree.children[1].children[1] if tree.children[1].node == TriggerTreeNode.FUNCTION_CALL else None

    ## check the type specified for the local exists
    if find(ctx.types, lambda k: k.name == local_type) == None:
        raise TranslationError(f"A local was declared with a type of {local_type} but that type does not exist.", tree.location)

    return StateParameter(tree.children[0].operator.strip(), local_type, tree.location, default_value)

def parseStateController(state: StateControllerSection, ctx: TranslationContext):
    ## determine the type of controller to be used
    if (state_name_node := find(state.properties, lambda k: k.key == "type")) == None:
        raise TranslationError(f"Could not find type property on state controller.", state.location)
    state_name = state_name_node.value.children[0] if state_name_node.value.node == TriggerTreeNode.MULTIVALUE else state_name_node.value
    if state_name.node != TriggerTreeNode.ATOM:
        raise TranslationError(f"The type property on a state controller must be a state controller name.", state_name.location)
    
    ## find the template definition corresponding to this controller
    if (state_template := find(ctx.templates, lambda k: k.name.lower() == state_name.operator.lower())) == None:
        raise TranslationError(f"Couldn't find any template or builtin controller with name {state_name.operator}.", state_name.location)
    
    ## process all triggers
    triggers: dict[int, List[TriggerTree]] = {}
    for trigger in state.properties:
        if (matched := re.match(r"trigger(all|[0-9]+)$", trigger.key.lower())) != None:
            # triggerall has group 0. otherwise just use the provided trigger group.
            group = matched.groups(0)[0]
            if group == "all": group = "0"
            group = int(group)
            # store the trigger in the specified group
            if group not in triggers: triggers[group] = []
            triggers[group].append(trigger.value)
    
    ## ensure the current state passes all required properties to the template
    props: dict[str, TriggerTree] = {}
    for prop in state_template.params:
        current_prop = find(state.properties, lambda k: k.key.lower() == prop.name.lower())
        if prop.required and current_prop == None:
            raise TranslationError(f"Required parameter {prop.name} for template or builtin controller {state_template.name} was not provided.", state.location)
        if current_prop != None:
            props[current_prop.key] = current_prop.value

    ## check if any property in the input does not exist on the target template, and emit a warning
    for prop_ in state.properties:
        if prop_.key.lower() == "type": continue
        if re.match(r"trigger(all|[0-9]+)$", prop_.key.lower()) != None: continue
        if find(state_template.params, lambda k: k.name.lower() == prop_.key.lower()) == None:
            print(f"Warning at {os.path.realpath(prop_.location.filename)}:{prop_.location.line}: Property {prop_.key} was passed to state controller or template named {state_template.name}, but the template does not declare this property.")
    
    return StateController(state_name.operator, triggers, props, state.location)

def findUndefinedGlobalsInTrigger(tree: TriggerTree, table: List[StateParameter], ctx: TranslationContext, autoEnums: List[TypeDefinition] = []) -> List[GlobalParameter]:
    if tree.node == TriggerTreeNode.ATOM:
        ## if the current node is an ATOM, check if the value is a number or a boolean.
        ## in those cases, the value is known.
        ## then, check if the name exists in the provided variable table.
        ## finally, check if the name exists in the trigger context. triggers which do not take parameters may optionally be used without brackets (e.g. `Alive` instead of `Alive()`)
        ## which would be parsed as an ATOM instead of a FUNCTION_CALL.
        if tryParseInt(tree.operator) != None or tryParseFloat(tree.operator) != None or tryParseBool(tree.operator) != None or tryParseCint(tree.operator) != None or tryParseString(tree.operator) != None:
            return []
        elif find(table, lambda k: k.name == tree.operator) != None:
            return []
        elif find(ctx.triggers, lambda k: k.name.lower() == tree.operator.lower() and len(k.params) == 0):
            return []
        elif find(ctx.types, lambda k: matchesEnumValue(k, tree.operator, autoEnums, tree.location)) != None:
            return []
        else:
            return [GlobalParameter(tree.operator, "")]
        
    result: List[GlobalParameter] = []

    ## for STRUCT_ACCESS, it is basically an ATOM which accesses a field. for purpose of finding globals we can just discard it.

    ## TODO: this needs to be able to handle FUNCTION_CALL with enum-type inputs (e.g. `gethitvar`)
    if tree.node == TriggerTreeNode.MULTIVALUE:
        ## for a multivalue case, we may be passed several autoEnum values for each value.
        subindex = 0
        for child in tree.children:
            if subindex < len(autoEnums):
                nextAutoEnum = [autoEnums[subindex]]
            elif len(autoEnums) != 0:
                nextAutoEnum = [autoEnums[-1]] ## for repetition operator
            else:
                nextAutoEnum = []
            subindex += 1
            result += findUndefinedGlobalsInTrigger(child, table, ctx, nextAutoEnum)
    else:
        for child in tree.children:
            result += findUndefinedGlobalsInTrigger(child, table, ctx, autoEnums)

    ## if this node is an assignment, and the LHS is for a globalparameter, get the type of the RHS.
    if len(result) > 0 and tree.node == TriggerTreeNode.BINARY_OP and tree.operator == ":=" and tree.children[0].node == TriggerTreeNode.ATOM:
        target = tree.children[0].operator
        rtype = runTypeCheck(tree.children[1], [TriggerParameter(p.name, p.type, p.location) for p in table], ctx)
        result += [GlobalParameter(target, rtype)]

    return result

def findUndefinedGlobals(state: StateController, table: List[StateParameter], ctx: TranslationContext) -> List[GlobalParameter]:
    result: List[GlobalParameter] = []

    ## identify the type of this controller
    controller_type = find(ctx.templates, lambda k: k.name.lower() == state.name.lower())
    if controller_type == None:
        raise TranslationError(f"Could not identify template or builtin definition for controller type {state.name}", state.location)

    ## search the trigger tree of each property and trigger in the controller to identify any undefined globals
    ## (essentially any ATOM which we do not recognize as an enum or flag, or existing variable)
    for name in state.properties:
        ## because a property has a known output type, we can retrieve the enum and flag names the property wants
        ## and pass them directly to runTypeCheck.
        ## for this we need to look up the expected result for this prop, and then unpack it into types,
        ## and determine any enums or flags to inject.
        expected_prop = find(controller_type.params, lambda k: k.name.lower() == name.lower())
        enums_flags: List[TypeDefinition] = []
        if expected_prop != None:
            expected_typedefs = unpackTypes(resolveAlias(expected_prop.type, ctx), ctx)
            if expected_typedefs != None:
                enums_flags = [td for td in expected_typedefs if td.category in [TypeCategory.FLAG, TypeCategory.ENUM, TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG]]
        result += findUndefinedGlobalsInTrigger(state.properties[name], table, ctx, enums_flags)
    for group in state.triggers:
        for trigger in state.triggers[group]:
            result += findUndefinedGlobalsInTrigger(trigger, table, ctx)

    return result

def makeFromAtom(value: str) -> Union[str, bool, int, float]:
    if (ivalue := tryParseInt(value)) != None:
        return ivalue
    elif (fvalue := tryParseFloat(value)) != None:
        return fvalue
    elif (bvalue := tryParseBool(value)) != None:
        return bvalue
    return value

def replaceVariableWithNameInTrigger(tree: TriggerTree, old_name: str, new_name: str):
    if tree.node == TriggerTreeNode.ATOM and tree.operator == old_name:
        tree.operator = new_name
    for child in tree.children:
        replaceVariableWithNameInTrigger(child, old_name, new_name)

def replaceVariableWithName(controller: StateController, old_name: str, new_name: str):
    for name in controller.properties:
        replaceVariableWithNameInTrigger(controller.properties[name], old_name, new_name)
    for group in controller.triggers:
        for trigger in controller.triggers[group]:
            replaceVariableWithNameInTrigger(trigger, old_name, new_name)

def replaceVariableWithExpressionInTrigger(tree: TriggerTree, old_name: str, new_exprn: TriggerTree):
    if tree.node == TriggerTreeNode.ATOM and tree.operator == old_name:
        tree.children = new_exprn.children
        tree.operator = new_exprn.operator
        tree.node = new_exprn.node
    for child in tree.children:
        replaceVariableWithExpressionInTrigger(child, old_name, new_exprn)

def replaceVariableWithExpression(controller: StateController, old_name: str, new_exprn: TriggerTree):
    for name in controller.properties:
        replaceVariableWithExpressionInTrigger(controller.properties[name], old_name, new_exprn)
    for group in controller.triggers:
        for trigger in controller.triggers[group]:
            replaceVariableWithExpressionInTrigger(trigger, old_name, new_exprn)

def combineTriggers(triggers: dict[int, List[TriggerTree]], location: Location) -> List[TriggerTree]:
    ## combines the provided trigger list into a single tree.
    ## this is mostly useful currently for merging templates into statedefs.
    ## but there's potential for this to be useful in some optimization strategy.

    results: List[TriggerTree] = []

    ## remember, group 0 is `triggerall`. we can add every trigger from group 0 directly to the result list.
    if 0 in triggers:
        results += triggers[0]

    ## for all other groups, we need to do something like:
    ## OR(AND(trigger1[0], trigger1[1], trigger1[2], ...), AND(trigger2[0], ...), ...)
    ## so the root is an OR, and the leaves are AND of all the triggers in 1 group.

    root = TriggerTree(TriggerTreeNode.BINARY_OP, "||", [], location)
    for index in triggers:
        if index == 0: continue
        leaf = TriggerTree(TriggerTreeNode.BINARY_OP, "&&", [], location)
        for trigger in triggers[index]:
            leaf.children.append(trigger)
        root.children.append(leaf)

    results += [root]

    return results

def tryReplaceTriggerCall(tree: TriggerTree, target: TriggerDefinition, locals: List[StateParameter], ctx: TranslationContext) -> bool:
    ## targets without expressions are builtin triggers, which never need replacement.
    if target.exprn == None: return False
    ## we will recursively try to find an ATOM or FUNCTION_CALL which matches the target definition.
    if tree.node == TriggerTreeNode.ATOM and tree.operator == target.name and len(target.params) == 0:
        tree.children = target.exprn.children
        tree.operator = target.exprn.operator
        tree.node = target.exprn.node
        return True
    if tree.node == TriggerTreeNode.FUNCTION_CALL and tree.operator == target.name:
        ## due to trigger overloading, we need to check param counts and type.
        ## FOR NOW, triggers have fixed parameter count.
        if len(target.params) != len(tree.children): return False
        convert_locals = [TriggerParameter(local.name, local.type) for local in locals]
        convert_globals = [TriggerParameter(g.name, g.type) for g in ctx.globals]
        auto_enums: List[TypeDefinition] = []
        expected_typedefs = unpackTypes(resolveAlias(target.type, ctx), ctx)
        if expected_typedefs != None:
            auto_enums = [td for td in expected_typedefs if td.category in [TypeCategory.FLAG, TypeCategory.ENUM, TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG]]
        for index in range(len(target.params)):
            resolved_type = runTypeCheck(tree.children[index], convert_locals + convert_globals, ctx, auto_enums)
            target_type = resolveAlias(target.params[index].type, ctx)
            if not unpackAndMatch(resolved_type, target_type, ctx):
                return False
                
        ## we must copy the target's tree, and do replacement of any parameters passed to the target.
        print(tree)
    
    ## analyse the children of the current tree recursively.
    updated = False
    for child in tree.children:
        updated = updated or tryReplaceTriggerCall(child, target, locals, ctx)

    return updated

def replaceTriggersInner(ctx: TranslationContext) -> bool:
    replaced = False

    ## iterate each controller within each statedef, and do replacements on each of:
    ### - triggers
    ### - properties
    ## this is a 5-ishx for-each loop, which is pretty bad. this can probably be done better. however the quantities we're working with
    ## mean it's probably more performant than it looks.
    for statedef in ctx.statedefs:
        for controller in statedef.states:
            for index in controller.triggers:
                for trigger in controller.triggers[index]:
                    for trigger_definition in ctx.triggers:
                        replaced = replaced or tryReplaceTriggerCall(trigger, trigger_definition, statedef.locals, ctx)


    return replaced

def replaceTriggers(ctx: TranslationContext):
    print("Start applying template replacements in statedefs...")
    ## wrapper for a function that repeatedly replaces triggers until no more triggers need replacing.
    ## this is because triggers can invoke other triggers in their definition, so one pass may not resolve every trigger.
    ## limit this to some number of iterations to prevent it from running forever.
    iterations = 0
    madeReplacement = True
    while madeReplacement:
        madeReplacement = replaceTriggersInner(ctx)
        iterations += 1
        if iterations > 20:
            raise TranslationError("Trigger replacement failed to complete after 20 iterations.", compiler_internal())
    print("Start completed template replacements")
        
def runTypeCheckGlobal(statedef: StateDefinition, ctx: TranslationContext):
    ## type check every property in a statedef.
    ## this is executed twice: once after template replace but before trigger replace,
    ## and then again after trigger replace.
    ## until trigger replacement happens we assume the output type of a defined trigger call is correct.
    globals_convert = [TriggerParameter(g.name, g.type, Location("<global-identifier>", 0)) for g in ctx.globals]
    locals_convert = [TriggerParameter(p.name, p.type, p.location) for p in statedef.locals]
    bool_type = find(ctx.types, lambda k: k.name == "bool")

    for controller in statedef.states:
        controller_type = find(ctx.templates, lambda k: k.name.lower() == controller.name.lower())
        if controller_type == None:
            raise TranslationError(f"Could not find any state controller or template with name {controller.name}.", controller.location)
        for group in controller.triggers:
            for trigger in controller.triggers[group]:
                result_type = runTypeCheck(trigger, globals_convert + locals_convert, ctx, isForTrigger = True)
                result_typedefs = unpackTypes(result_type, ctx)
                if result_typedefs == None:
                    raise TranslationError(f"Could not find any type with descriptor {result_type}.", trigger.location)
                if len(result_typedefs) != 1:
                    raise TranslationError(f"Result of trigger expression must be bool, not a tuple {result_type}.", trigger.location)
                if not typeConvertOrdered(result_typedefs[0], bool_type, ctx, trigger.location): # type: ignore
                    raise TranslationError(f"Result of trigger expression must be bool, not {result_type}.", trigger.location)
        for prop in controller.properties:
            ## because a property has a known output type, we can retrieve the enum and flag names the property wants
            ## and pass them directly to runTypeCheck.
            ## for this we need to look up the expected result for this prop, and then unpack it into types,
            ## and determine any enums or flags to inject.
            expected_prop = find(controller_type.params, lambda k: k.name.lower() == prop)
            enums_flags: List[TypeDefinition] = []
            if expected_prop != None:
                expected_typedefs = unpackTypes(resolveAlias(expected_prop.type, ctx), ctx)
                if expected_typedefs != None:
                    enums_flags = [td for td in expected_typedefs if td.category in [TypeCategory.FLAG, TypeCategory.ENUM, TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG]]

            result_type = runTypeCheck(controller.properties[prop], globals_convert + locals_convert, ctx, enums_flags)
            result_typedefs = unpackTypes(resolveAlias(result_type, ctx), ctx)
            if result_typedefs == None:
                raise TranslationError(f"Could not find any type with descriptor {result_type}.", controller.properties[prop].location)            
            
            ## expected_prop could be None if the prop isn't expected on this controller/template.
            ## we already emitted a warning for this earlier anyway.
            if expected_prop != None:
                if not unpackAndMatch(resolveAlias(result_type, ctx), resolveAlias(expected_prop.type, ctx), ctx):
                    raise TranslationError(f"Could not match type {result_type} to expected type {expected_prop.type} on controller {controller_type.name}.", controller.properties[prop].location)
        
def createGlobalsTable(ctx: TranslationContext):
    ## we must iterate all statedefs and search for undefined globals.
    ## this should also include a type checking stage.
    ## we type-check here because this is the only stage we can type-check with original defined trigger names.
    discovered: List[GlobalParameter] = []
    location: dict[str, Location] = {}
    for statedef in ctx.statedefs:
        for controller in statedef.states:
            partial = findUndefinedGlobals(controller, statedef.locals, ctx)
            ## each symbol in `partial` may already exist in `discovered` from a previous controller.
            ## each symbol may have an empty type (when it is used) or a concrete type (when it is assigned).
            ## `partial` itself can also contain duplicates (if it is used, assigned, re-assigned in the same controller).
            ## we want to add new entries to partial, update entries from empty to concrete, and confirm two concrete assignments have matching types.
            for symbol in partial:
                ## if not in discovered already, add it
                if (matching := find(discovered, lambda k: k.name == symbol.name)) == None:
                    discovered.append(symbol)
                    location[symbol.name] = controller.location
                    continue
                ## if in discovered and this symbol has empty type, skip
                if symbol.type == "": continue
                ## if in discovered with empty type, update
                if matching.type == "":
                    matching.type = symbol.type
                    location[symbol.name] = controller.location
                    continue
                ## if both are concrete, attempt to match
                type1 = find(ctx.types, lambda k: k.name == symbol.type)
                type2 = find(ctx.types, lambda k: k.name == matching.type) # type: ignore
                if type1 == None:
                    raise TranslationError(f"Could not find type with name {type1} during type checking.", controller.location)
                if type2 == None:
                    raise TranslationError(f"Could not find type with name {type2} during type checking.", controller.location)
                if not typeConvertWidest(type1, type2, ctx, controller.location):
                    raise TranslationError(f"Global {symbol.name} was previously assigned with type {type1}, but was re-assigned with incompatible type {type2}.", controller.location)
    ## now ensure every symbol has a concrete type.
    for sym in discovered:
        if sym.type == "":
            raise TranslationError(f"Global {sym.name} was used, but never assigned, so the type checker could not identify its type.", location[sym.name])
    ## global table has now been created. store in ctx and run the full type check
    ctx.globals = discovered
    for statedef in ctx.statedefs:
        runTypeCheckGlobal(statedef, ctx)

def replaceTemplatesInner(ctx: TranslationContext) -> bool:
    replaced = False

    ## process each statedef and each controller within the statedefs
    ## if a controller's `type` property references a non-builtin template, remove
    ## that controller from the state list and insert all the controllers from the template.
    ## if no template at all matches, raise an error.
    for statedef in ctx.statedefs:
        index = 0
        while index < len(statedef.states):
            controller = statedef.states[index]
            if (template := find(ctx.templates, lambda k: k.name.lower() == controller.name.lower())) == None:
                raise TranslationError(f"No template or builtin controller was found to match state controller with name {controller.name}", controller.location)
            ## we only care about DEFINED templates here. BUILTIN templates are for MUGEN/CNS state controller types.
            if template.category == TemplateCategory.DEFINED:
                replaced = True
                ## 1. copy all the locals declared in the template to the locals of the state, with a prefix to ensure they are uniquified.
                local_prefix = f"{generate_random_string(8)}_"
                local_map: dict[str, str] = {}
                for local in template.locals:
                    statedef.locals.append(StateParameter(f"{local_prefix}{local.name}", local.type, local.location, local.default))
                    local_map[local.name] = f"{local_prefix}{local.name}"
                ## 2. copy all controllers from the template, updating uses of the locals to use the new prefix.
                new_controllers = copy.deepcopy(template.states)
                for new_controller in new_controllers:
                    for local_name in local_map:
                        replaceVariableWithName(new_controller, local_name, local_map[local_name])
                ## 3. replace all uses of parameters with the expression to substitute for that parameter.
                exprn_map: dict[str, TriggerTree] = {}
                for param in template.params:
                    target_exprn = controller.properties[param.name] if param.name in controller.properties else None
                    if target_exprn == None and param.required:
                        raise TranslationError(f"No expression was provided for parameter with name {param.name} on template or controller {controller.name}.", controller.location)
                    if target_exprn != None:
                        exprn_map[param.name] = target_exprn
                for new_controller in new_controllers:
                    for exprn_name in exprn_map:
                        replaceVariableWithExpression(new_controller, exprn_name, exprn_map[exprn_name])

                ## 4. combine the triggers on the template call into one or more triggerall statements and insert into each new controller.
                combinedTriggers = combineTriggers(controller.triggers, controller.location)
                for new_controller in new_controllers:
                    if 0 not in new_controller.triggers:
                        new_controller.triggers[0] = []
                    new_controller.triggers[0] += combinedTriggers

                ## 5. remove the call to the template (at `index`) and insert the new controllers into the statedef
                statedef.states = statedef.states[:index] + new_controllers + statedef.states[index+1:]
                index += len(new_controllers)
                
            index += 1

    return replaced

def replaceTemplates(ctx: TranslationContext):
    ## wrapper for a function that repeatedly replaces templates until no more templates need replacing.
    ## this is because templates can invoke other templates in their definition, so one pass may not resolve every template.
    ## limit this to some number of iterations to prevent it from running forever.
    print("Start applying template replacements in statedefs...")
    iterations = 0
    madeReplacement = True
    while madeReplacement:
        madeReplacement = replaceTemplatesInner(ctx)
        iterations += 1
        if iterations > 20:
            raise TranslationError("Template replacement failed to complete after 20 iterations.", compiler_internal())
    print("Successfully completed template replacement.")

def preTranslateStateDefinitions(load_ctx: LoadContext, ctx: TranslationContext):
    print("Start first-pass state definition processing...")
    ## this does a very early portion of statedef translation.
    ## essentially it just builds a StateDefinition object from each StateDefinitionSection object.
    ## this makes it easier to do the next tasks (template/trigger replacement).
    for state_definition in load_ctx.state_definitions:
        ## in current MTL standard state_name is just the state ID.
        state_name = state_definition.name
        ## identify all parameters which can be set on the statedef
        state_params = StateDefinitionParameters()
        for prop in state_definition.props:
            ## allow-list the props which can be set here to avoid evil behaviour
            if prop.key.lower() in ["type", "movetype", "physics", "anim", "ctrl", "poweradd", "juggle", "facep2", "hitdefpersist", "movehitpersist", "hitcountpersist", "sprpriority"]:
                setattr(state_params, prop.key.lower(), makeFromAtom(prop.value))
        ## identify all local variable declarations, if any exist
        state_locals: list[StateParameter] = []
        for prop in state_definition.props:
            if prop.key.lower() == "local":
                state_locals.append(parseLocalParameter(prop, ctx))
        ## pull the list of controllers; we do absolutely zero checking or validation at this stage.
        state_controllers: list[StateController] = []
        for state in state_definition.states:
            controller = parseStateController(state, ctx)
            state_controllers.append(controller)

        ctx.statedefs.append(StateDefinition(state_name, state_params, state_locals, state_controllers, state_definition.location))
    print(f"Successfully resolved {len(ctx.statedefs)} state definitions")

def translateTemplates(load_ctx: LoadContext, ctx: TranslationContext):
    print("Start loading template definitions...")
    for template_definition in load_ctx.templates:
        ## determine final template name and check if it is already in use.
        template_name = template_definition.name if template_definition.namespace == None else f"{template_definition.namespace}.{template_definition.name}"
        if (original := find(ctx.templates, lambda k: k.name == template_name)) != None:
            raise TranslationError(f"Template with name {template_name} was redefined: original definition at {original.location.filename}:{original.location.line}", template_definition.location)
        
        ## determine the type and default value of any local declarations
        template_locals: list[StateParameter] = []
        for local in template_definition.locals:
            template_locals.append(parseLocalParameter(local, ctx))

        ## determine the type of any parameter declarations
        template_params: list[TemplateParameter] = []
        if template_definition.params != None:
            for param in template_definition.params.properties:
                if find(ctx.types, lambda k: k.name == param.value) == None:
                    raise TranslationError(f"A template parameter was declared with a type of {param.value} but that type does not exist.", param.location)
                template_params.append(TemplateParameter(param.key, param.value))

        ## analyse all template states. in this stage we just want to confirm variable usage is correct.
        ## type checking will happen later when we have substituted templates into their call sites.
        template_states: list[StateController] = []
        for state in template_definition.states:
            controller = parseStateController(state, ctx)
            ## run findUndefinedGlobals against this controller to determine any global variable usage.
            ## the variable table we pass contains only the locals and the parameters, so all globals in this case are undefined.
            ## templates which use undefined global variables will be rejected as templates can't use globals.
            ## we must also pass the list of triggers so the function can identify parameter-less trigger calls.
            temp_params = [StateParameter(p.name, p.type, p.location, None) for p in template_params]
            undefineds = findUndefinedGlobals(controller, temp_params + template_locals, ctx)
            if len(undefineds) != 0:
                raise TranslationError(f"Template uses global variables named {', '.join([u.name for u in undefineds])}, but templates cannot define or use globals.", state.location)
            template_states.append(controller)
        
        ctx.templates.append(TemplateDefinition(template_name, template_params, template_locals, template_states, template_definition.location))
    print(f"Successfully resolved {len(ctx.templates)} template definitions")

def translateTriggers(load_ctx: LoadContext, ctx: TranslationContext):
    print("Start loading trigger function definitions...")
    for trigger_definition in load_ctx.triggers:
        trigger_name = trigger_definition.name if trigger_definition.namespace == None else f"{trigger_definition.namespace}.{trigger_definition.name}"
        
        if (matching_type := find(ctx.types, lambda k: k.name == trigger_name)) != None:
            raise TranslationError(f"Trigger with name {trigger_name} overlaps type name defined at {matching_type.location.filename}:{matching_type.location.line}: type names are reserved for type initialization.", trigger_definition.location)
        
        # identify matches by name, then inspect type signature
        param_types = [param.value for param in trigger_definition.params.properties] if trigger_definition.params != None else []
        matched = findTriggerBySignature(trigger_name, param_types, ctx, trigger_definition.location)
                
        if matched != None:
            raise TranslationError(f"Trigger with name {trigger_name} was redefined: original definition at {matched.location.filename}:{matched.location.line}", trigger_definition.location)
        
        ## ensure the expected type of the trigger is known
        if (trigger_type := find(ctx.types, lambda k: k.name == trigger_definition.type)) == None:
            raise TranslationError(f"Trigger with name {trigger_name} declares a return type of {trigger_definition.type} but that type is not known.", trigger_definition.location)
        
        ## ensure the type of all parameters for the trigger are known
        params: List[TriggerParameter] = []
        if trigger_definition.params != None:
            for parameter in trigger_definition.params.properties:
                if (matching_type := find(ctx.types, lambda k: k.name == parameter.value)) == None:
                    raise TranslationError(f"Trigger parameter {parameter.key} declares a type of {parameter.value} but that type is not known.", parameter.location)
                params.append(TriggerParameter(parameter.key, parameter.value))

        ## run the type-checker against the trigger expression
        ## the locals table for triggers is just the input params.
        result_type = runTypeCheck(trigger_definition.value, params, ctx, isForTrigger = True)
        if not unpackAndMatch(result_type, trigger_type.name, ctx):
            raise TranslationError(f"Could not match type {result_type} to expected type {trigger_type.name} on trigger {trigger_name}.", trigger_definition.location)

        ctx.triggers.append(TriggerDefinition(trigger_name, trigger_type.name, None, params, trigger_definition.value, trigger_definition.location))
    print(f"Successfully resolved {len(ctx.triggers)} trigger function definitions")

def translateStructs(load_ctx: LoadContext, ctx: TranslationContext):
    for struct_definition in load_ctx.struct_definitions:
        ## determine final type name and check if it is already in use.
        type_name = struct_definition.name if struct_definition.namespace == None else f"{struct_definition.namespace}.{struct_definition.name}"
        if (original := find(ctx.types, lambda k: k.name == type_name)) != None:
            raise TranslationError(f"Type with name {type_name} was redefined: original definition at {original.location.filename}:{original.location.line}", struct_definition.location)
        
        ## check that all members of the struct are known types
        ## also, sum the total size of the structure.
        struct_size = 0
        struct_members: List[str] = []
        for member_name in struct_definition.members.properties:
            if (member := find(ctx.types, lambda k: k.name == member_name.value)) == None:
                raise TranslationError(f"Member {member_name.key} on structure {type_name} has type {member_name.value}, but this type does not exist.", member_name.location)
            struct_size += member.size
            struct_members.append(f"{member_name.key}:{member.name}")
        
        ## append this to the type list, in translation context we make no distincition between structures and other types.
        ctx.types.append(TypeDefinition(type_name, TypeCategory.STRUCTURE, struct_size, struct_members, struct_definition.location))
    print(f"Successfully resolved {len(ctx.types)} type and structure definitions")

def translateTypes(load_ctx: LoadContext, ctx: TranslationContext):
    print(f"Start processing type definitions...")
    for type_definition in load_ctx.type_definitions:
        ## determine final type name and check if it is already in use.
        type_name = type_definition.name if type_definition.namespace == None else f"{type_definition.namespace}.{type_definition.name}"
        if (original := find(ctx.types, lambda k: k.name == type_name)) != None:
            raise TranslationError(f"Type with name {type_name} was redefined: original definition at {original.location.filename}:{original.location.line}", type_definition.location)

        ## determine the type category and type members
        if type_definition.type.lower() == "alias":
            type_category = TypeCategory.ALIAS
            if (alias := find(type_definition.properties, lambda k: k.key.lower() == "source")) == None:
                raise TranslationError(f"Alias type {type_name} must specify an alias source.", type_definition.location)
            if (source := unpackTypes(alias.value, ctx)) == None: # type: ignore
                raise TranslationError(f"Alias type {type_name} references source definition {alias.value}, but the definition could not be resolved.", alias.location)
            type_members = [alias.value]
            target_size = 0
            for s in source:
                target_size += s.size
        elif type_definition.type.lower() == "union":
            type_category = TypeCategory.UNION
            type_members: List[str] = []
            target_size = -1
            for property in type_definition.properties:
                if property.key == "member":
                    if (target := find(ctx.types, lambda k: k.name == property.value)) == None:
                        raise TranslationError(f"Union type {type_name} references source type {property.value}, but that type does not exist.", type_definition.location)
                    if target_size == -1:
                        target_size = target.size
                    if target.size != target_size:
                        raise TranslationError(f"Union type {type_name} has member size {target_size} but attempted to include type {target.name} with mismatched size {target.size}.", property.location)
                    type_members.append(target.name)
            if len(type_members) == 0:
                raise TranslationError(f"Union type {type_name} must specify at least one member.", type_definition.location)
        elif type_definition.type.lower() == "enum":
            type_category = TypeCategory.ENUM
            type_members: List[str] = []
            for property in type_definition.properties:
                if property.key == "enum":
                    type_members.append(property.value)
            target_size = 32
        elif type_definition.type.lower() == "flag":
            type_category = TypeCategory.FLAG
            type_members: List[str] = []
            for property in type_definition.properties:
                if property.key == "flag":
                    type_members.append(property.value)
            if len(type_members) > 32:
                raise TranslationError("Flag types may not support more than 32 members.", type_definition.location)
            target_size = 32
        else:
            raise TranslationError(f"Unrecognized type category {type_definition.type} in Define Type section.", type_definition.location)
        
        ctx.types.append(TypeDefinition(type_name, type_category, target_size, type_members, type_definition.location))

def translateContext(load_ctx: LoadContext) -> TranslationContext:
    ctx = TranslationContext(load_ctx.filename)

    ctx.types = builtins.getBaseTypes()
    ctx.triggers = builtins.getBaseTriggers()
    ctx.templates = builtins.getBaseTemplates()

    translateTypes(load_ctx, ctx)
    translateStructs(load_ctx, ctx)
    translateTriggers(load_ctx, ctx)
    translateTemplates(load_ctx, ctx)

    ## add the default parameters ignorehitpause and persistent to all template definitions.
    for template in ctx.templates:
        template.params.append(TemplateParameter("ignorehitpause", "bool", False))
        template.params.append(TemplateParameter("persistent", "int", False))

    preTranslateStateDefinitions(load_ctx, ctx)
    replaceTemplates(ctx)

    for statedef in ctx.statedefs:
        if len(statedef.states) > 512:
            raise TranslationError(f"State definition for state {statedef.name} has more than 512 state controllers after template resolution. Reduce the size of this state definition or its templates.", statedef.location)
        
    createGlobalsTable(ctx)
    replaceTriggers(ctx)

    return ctx

if __name__ == "__main__":
    ## TODO: need a project file. need to be able to parse AIR, SPR, SND and multiple MTL/CNS files.
    parser = argparse.ArgumentParser(prog='mtlcc', description='Translation tool from MTL templates into CNS character code')
    parser.add_argument('input', help='Path to the MTL template to translate')

    args = parser.parse_args()
    ## note: the spec states that translation of included files should stop at step 3.
    ## this is guaranteed by having steps up to 3 in `loadFile`, and remaining steps handled in `translateContext`.
    try:
        loadContext = loadFile(args.input, [])
        translated = translateContext(loadContext)
    except TranslationError as exc:
        py_exc = traceback.format_exc().split("\n")[-4].strip()
        print("Translation terminated with an error.")
        print(f"\t{exc.message}")
        print(f"mtlcc exception source: {py_exc}")