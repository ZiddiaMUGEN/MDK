import argparse
import os
import re
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
            statedef = StateDefinitionSection(section.name[9:], section.properties, section.filename, section.line)
            ctx.state_definitions.append(statedef)

            while index + 1 < len(sections) and sections[index + 1].name.lower().startswith("state "):
                properties: List[StateControllerProperty] = []
                for property in sections[index + 1].properties:
                    properties.append(StateControllerProperty(property.key, trigger.parseTrigger(property.value, property.filename, property.line)))
                statedef.states.append(StateControllerSection(properties, sections[index + 1].filename, sections[index + 1].line))
                index += 1
        elif section.name.lower().startswith("include"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Include sections.", section.filename, section.line)
            ctx.includes.append(section)
        elif section.name.lower().startswith("define type"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.filename, section.line)
            
            if (name := find(section.properties, lambda k: k.key.lower() == "name")) == None:
                raise TranslationError("Define Type section must provide a name property.", section.filename, section.line)
        
            if (type := find(section.properties, lambda k: k.key.lower() == "type")) == None:
                raise TranslationError("Define Type section must provide a type property.", section.filename, section.line)

            ctx.type_definitions.append(TypeDefinitionSection(name.value, type.value, section.properties, section.filename, section.line))
        elif section.name.lower().startswith("define template"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.filename, section.line)
            
            if (prop := find(section.properties, lambda k: k.key.lower() == "name")) == None:
                raise TranslationError("Define Template section must provide a name property.", section.filename, section.line)
            
            template = TemplateSection(prop.value, section.filename, section.line)
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
                        properties.append(StateControllerProperty(property.key, trigger.parseTrigger(property.value, property.filename, property.line)))
                    template.states.append(StateControllerSection(properties, sections[index + 1].filename, sections[index + 1].line))
                elif sections[index + 1].name.lower().startswith("define parameters"):
                    if template.params != None:
                        raise TranslationError("A Define Template section may only contain 1 Define Parameters subsection.", sections[index + 1].filename, sections[index + 1].line)
                    else:
                        template.params = sections[index + 1]
                else:
                    break
                index += 1
        elif section.name.lower().startswith("define trigger"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.filename, section.line)
            
            if (name := find(section.properties, lambda k: k.key.lower() == "name")) == None:
                raise TranslationError("Define Trigger section must provide a name property.", section.filename, section.line)
            if (type := find(section.properties, lambda k: k.key.lower() == "type")) == None:
                raise TranslationError("Define Trigger section must provide a type property.", section.filename, section.line)
            if (value := find(section.properties, lambda k: k.key.lower() == "value")) == None:
                raise TranslationError("Define Trigger section must provide a value property.", section.filename, section.line)

            trigger_section = TriggerSection(name.value, type.value, trigger.parseTrigger(value.value, value.filename, value.line), section.filename, section.line)
            ctx.triggers.append(trigger_section)
            if index + 1 < len(sections) and sections[index + 1].name.lower().startswith("define parameters"):
                trigger_section.params = sections[index + 1]
                index += 1
        elif section.name.lower().startswith("define structure"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.filename, section.line)

            if index + 1 >= len(sections) or not sections[index + 1].name.lower().startswith("define members"):
                raise TranslationError("A Define Structure section must be followed immediately by a Define Members section.", section.filename, section.line)
            
            if (prop := find(section.properties, lambda k: k.key.lower() == "name")) == None:
                raise TranslationError("Define Structure section must provide a name property.", section.filename, section.line)

            structure = StructureDefinitionSection(prop.value, sections[index + 1], section.filename, section.line)
            ctx.struct_definitions.append(structure)
            index += 1
        elif section.name.lower().startswith("state "):
            # a standalone 'state' section is invalid. raise an exception
            raise TranslationError("A State section in a source file must be grouped with a parent section such as Statedef.", section.filename, section.line)
        elif section.name.lower().startswith("define parameters"):
            # a standalone 'state' section is invalid. raise an exception
            raise TranslationError("A Define Parameters section in a source file must be grouped with a parent section such as Define Template.", section.filename, section.line)
        elif section.name.lower().startswith("define members"):
            # a standalone 'state' section is invalid. raise an exception
            raise TranslationError("A Define Members section in a source file must be grouped with a parent Define Structure section.", section.filename, section.line)
        else:
            raise TranslationError(f"Section with name {section.name} was not recognized by the parser.", section.filename, section.line)
        index += 1

def processIncludes(mode: TranslationMode, cycle: List[str], ctx: LoadContext):
    # CNS mode does not support Include sections.
    if mode == TranslationMode.CNS_MODE:
        return
    
    for include in ctx.includes:
        if (source := find(include.properties, lambda k: k.key.lower() == "source")) == None:
            raise TranslationError("Include block must define a `source` property indicating the file to be included.", include.filename, include.line)
        
        ## per the standard, we search 3 locations for the source file:
        ## - working directory
        ## - directory of the file performing the inclusion
        ## - directory of this file
        ## - absolute path
        search = [f"{os.getcwd()}/{source.value}", f"{os.path.dirname(os.path.realpath(include.filename))}/{source.value}", f"{os.path.dirname(os.path.realpath(__file__))}/{source.value}", f"{os.path.realpath(source.value)}"]
        location: Optional[str] = None
        for path in search:
            if os.path.exists(path):
                location = path
                break
        if location == None:
            raise TranslationError(f"Could not find the source file specified by {source.value} for inclusion.", include.filename, include.line)
        
        ## now translate the source file
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
                    print(f"Warning at {os.path.realpath(property.filename)}:{property.line}: Attempted to import name {property.value} from included file {include.filename} but no such name exists.")

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
        raise TranslationError("A cycle was detected during include processing.", file, 0)

    ctx = LoadContext(file)

    with open(file) as f:
        contents = ini.parse(f.read(), ctx.ini_context)

    mode = TranslationMode.MTL_MODE if file.endswith(".mtl") or file.endswith(".inc") else TranslationMode.CNS_MODE
    parseTarget(contents, mode, ctx)
    processIncludes(mode, cycle, ctx)

    return ctx

def findTriggerBySignature(name: str, types: List[str], ctx: TranslationContext, filename: str, line: int) -> Union[TriggerDefinition, None]:
    matches = list(filter(lambda k: k.name == name, ctx.triggers))

    # iterate each match
    for match in matches:
        if len(match.params) != len(types): continue
        
        is_matching = True
        for index in range(len(types)):
            first_str = resolveAlias(types[index], ctx, [])
            first = find(ctx.types, lambda k: k.name == first_str)
            second_str = resolveAlias(match.params[index].type, ctx, [])
            second = find(ctx.types, lambda k: k.name == second_str)
            assert(first != None and second != None)
            if typeConvertOrdered(first, second, ctx, filename, line) == None:
                is_matching = False

        if is_matching: return match

    return None

def runTypeCheck(tree: TriggerTree, filename: str, line: int, locals: List[TriggerParameter], ctx: TranslationContext) -> str:
    ## for multivalue, just handle single case for now. tuples are a bit of work still.
    if tree.node == TriggerTreeNode.MULTIVALUE and len(tree.children) > 1:
        raise TranslationError("TODO: support multivalue expressions correctly", filename, line)
    elif tree.node == TriggerTreeNode.MULTIVALUE:
        return runTypeCheck(tree.children[0], filename, line, locals, ctx)
    
    ## for intervals, give an error for now.
    if tree.node == TriggerTreeNode.INTERVAL_OP:
        raise TranslationError("TODO: support interval expressions correctly", filename, line)
    
    ## for atoms, early exit: just identify the type of the node.
    if tree.node == TriggerTreeNode.ATOM:
        if tryParseInt(tree.operator) != None:
            return "int"
        elif tryParseFloat(tree.operator) != None:
            return "float"
        elif tryParseBool(tree.operator) != None:
            return "bool"
        elif (local := find(locals, lambda k: k.name == tree.operator)) != None:
            return resolveAlias(local.type, ctx, [])
        else:
            raise TranslationError(f"Could not determine type from expression {tree.operator}.", filename, line)
    
    ## do a depth-first search on the tree. determine the type of each node, then apply types to each operator to determine the result type.
    child_types: List[str] = []
    for child in tree.children:
        child_types.append(runTypeCheck(child, filename, line, locals, ctx))

    ## process operators using operator functions.
    ## no need to evaluate anything at this stage, just return the stated return type of the operator.
    if tree.node == TriggerTreeNode.UNARY_OP or tree.node == TriggerTreeNode.BINARY_OP:
        ## operator is stored in tree.operator, child types are above. there are builtin operator triggers provided,
        ## so determine which trigger to use.
        operator_call = findTriggerBySignature(f"operator{tree.operator}", child_types, ctx, filename, line)
        if operator_call == None:
            raise TranslationError(f"Could not find any matching overload for operator {tree.operator} with input types {', '.join(child_types)}.", filename, line)
        return resolveAlias(operator_call.type, ctx, [])

    ## handle explicit function calls.
    ## this is very similar to operators. find the matching trigger and use the output type provided.
    if tree.node == TriggerTreeNode.FUNCTION_CALL:
        function_call = findTriggerBySignature(tree.operator, child_types, ctx, filename, line)
        if function_call == None:
            raise TranslationError(f"Could not find any matching overload for trigger {tree.operator} with input types {', '.join(child_types)}.", filename, line)
        return resolveAlias(function_call.type, ctx, [])
    
    return "bottom"

def parseLocalParameter(local: INIProperty, ctx: TranslationContext) -> StateParameter:
    ## local variables are basically specified as valid trigger syntax, e.g. `myLocalName = myLocalType(defaultValueExpr)`
    ## so we parse as a trigger and make sure the syntax tree matches the expected format.
    ## there are only 2 valid formats: `name = type` and `name = type(default)`.
    tree = trigger.parseTrigger(local.value, local.filename, local.line)
    if tree.node == TriggerTreeNode.MULTIVALUE: tree = tree.children[0]

    ## check the operator is correct and the first node is an atom
    ## keep in mind the tree constructs right-to-left so children[1] is the first child node.
    if tree.node != TriggerTreeNode.BINARY_OP or tree.operator != "=":
        raise TranslationError("Local definitions must follow the format <local name> = <local type>(<optional default>).", local.filename, local.line)
    if tree.children[1].node != TriggerTreeNode.ATOM:
        raise TranslationError("Local definitions must follow the format <local name> = <local type>(<optional default>).", local.filename, local.line)
    ## the second node can be either ATOM (for type name) or FUNCTION_CALL with a single child (for default value)
    if tree.children[0].node != TriggerTreeNode.ATOM and tree.children[0].node != TriggerTreeNode.FUNCTION_CALL:
        raise TranslationError("Local definitions must follow the format <local name> = <local type>(<optional default>).", local.filename, local.line)
    if tree.children[0].node == TriggerTreeNode.FUNCTION_CALL and len(tree.children[0].children) != 1:
        raise TranslationError("Local definitions must follow the format <local name> = <local type>(<optional default>).", local.filename, local.line)
    local_type = tree.children[0].operator
    default_value = tree.children[0].children[0] if tree.children[0].node == TriggerTreeNode.FUNCTION_CALL else None

    ## check the type specified for the local exists
    if find(ctx.types, lambda k: k.name == local_type) == None:
        raise TranslationError(f"A local was declared with a type of {local_type} but that type does not exist.", local.filename, local.line)

    return StateParameter(tree.children[1].operator.strip(), local_type, default_value)

def parseStateController(state: StateControllerSection, ctx: TranslationContext):
    ## determine the type of controller to be used
    if (state_name_node := find(state.properties, lambda k: k.key == "type")) == None:
        raise TranslationError(f"Could not find type property on state controller.", state.filename, state.line)
    state_name = state_name_node.value.children[0] if state_name_node.value.node == TriggerTreeNode.MULTIVALUE else state_name_node.value
    if state_name.node != TriggerTreeNode.ATOM:
        raise TranslationError(f"The type property on a state controller must be a state controller name.", state.filename, state.line)
    
    ## find the template definition corresponding to this controller
    if (state_template := find(ctx.templates, lambda k: k.name.lower() == state_name.operator.lower())) == None:
        raise TranslationError(f"Couldn't find any template or builtin controller with name {state_name.operator}.", state.filename, state.line)
    
    ## process all triggers
    triggers: dict[int, List[TriggerTree]] = {}
    for trigger in state.properties:
        if (matched := re.match(r"trigger(all|[0-9]+)$", trigger.key)) != None:
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
            raise TranslationError(f"Required parameter {prop.name} for template or builtin controller {state_template.name} was not provided.", state.filename, state.line)
        if current_prop != None:
            props[current_prop.key] = current_prop.value
    
    return StateController(state_name.operator, triggers, props)

def findUndefinedGlobalsInTrigger(tree: TriggerTree, table: List[StateParameter], triggers: List[TriggerDefinition]) -> List[str]:
    if tree.node == TriggerTreeNode.ATOM:
        ## if the current node is an ATOM, check if the value is a number or a boolean.
        ## in those cases, the value is known.
        ## then, check if the name exists in the provided variable table.
        ## finally, check if the name exists in the trigger context. triggers which do not take parameters may optionally be used without brackets (e.g. `Alive` instead of `Alive()`)
        ## which would be parsed as an ATOM instead of a FUNCTION_CALL.
        if tryParseInt(tree.operator) != None or tryParseFloat(tree.operator) != None or tryParseBool(tree.operator) != None:
            return []
        elif find(table, lambda k: k.name == tree.operator) != None:
            return []
        elif find(triggers, lambda k: k.name.lower() == tree.operator.lower() and len(k.params) == 0):
            return []
        else:
            return [tree.operator]
        
    result: List[str] = []
    for child in tree.children:
        result += findUndefinedGlobalsInTrigger(child, table, triggers)

    return result

def findUndefinedGlobals(state: StateController, table: List[StateParameter], triggers: List[TriggerDefinition]) -> List[str]:
    result: List[str] = []

    ## search the trigger tree of each property and trigger in the controller to identify any undefined globals
    ## (essentially any ATOM which we do not recognize as an enum or flag, or existing variable)
    for name in state.properties:
        result += findUndefinedGlobalsInTrigger(state.properties[name], table, triggers)
    for group in state.triggers:
        for trigger in state.triggers[group]:
            result += findUndefinedGlobalsInTrigger(trigger, table, triggers)

    return result

def translateTemplates(load_ctx: LoadContext, ctx: TranslationContext):
    for template_definition in load_ctx.templates:
        ## determine final template name and check if it is already in use.
        template_name = template_definition.name if template_definition.namespace == None else f"{template_definition.namespace}.{template_definition.name}"
        if (original := find(ctx.templates, lambda k: k.name == template_name)) != None:
            raise TranslationError(f"Template with name {template_name} was redefined: original definition at {original.filename}:{original.line}", template_definition.filename, template_definition.line)
        
        ## determine the type and default value of any local declarations
        template_locals: list[StateParameter] = []
        for local in template_definition.locals:
            template_locals.append(parseLocalParameter(local, ctx))

        ## determine the type of any parameter declarations
        template_params: list[TemplateParameter] = []
        if template_definition.params != None:
            for param in template_definition.params.properties:
                if find(ctx.types, lambda k: k.name == param.value) == None:
                    raise TranslationError(f"A template parameter was declared with a type of {param.value} but that type does not exist.", param.filename, param.line)
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
            temp_params = [StateParameter(p.name, p.type, None) for p in template_params]
            undefineds = findUndefinedGlobals(controller, temp_params + template_locals, ctx.triggers)
            if len(undefineds) != 0:
                raise TranslationError(f"Template uses global variables named {', '.join(undefineds)}, but templates cannot define or use globals.", state.filename, state.line)
            template_states.append(controller)
        
        ctx.templates.append(TemplateDefinition(template_name, template_params, template_locals, template_states, template_definition.filename, template_definition.line))

def translateTriggers(load_ctx: LoadContext, ctx: TranslationContext):
    for trigger_definition in load_ctx.triggers:
        trigger_name = trigger_definition.name if trigger_definition.namespace == None else f"{trigger_definition.namespace}.{trigger_definition.name}"
        
        if (matching_type := find(ctx.types, lambda k: k.name == trigger_name)) != None:
            raise TranslationError(f"Trigger with name {trigger_name} overlaps type name defined at {matching_type.filename}:{matching_type.line}: type names are reserved for type initialization.", trigger_definition.filename, trigger_definition.line)
        
        # identify matches by name, then inspect type signature
        param_types = [param.value for param in trigger_definition.params.properties] if trigger_definition.params != None else []
        matched = findTriggerBySignature(trigger_name, param_types, ctx, trigger_definition.filename, trigger_definition.line)
                
        if matched != None:
            raise TranslationError(f"Trigger with name {trigger_name} was redefined: original definition at {matched.filename}:{matched.line}", trigger_definition.filename, trigger_definition.line)
        
        ## ensure the expected type of the trigger is known
        if (trigger_type := find(ctx.types, lambda k: k.name == trigger_definition.type)) == None:
            raise TranslationError(f"Trigger with name {trigger_name} declares a return type of {trigger_definition.type} but that type is not known.", trigger_definition.filename, trigger_definition.line)
        
        ## ensure the type of all parameters for the trigger are known
        params: List[TriggerParameter] = []
        if trigger_definition.params != None:
            for parameter in trigger_definition.params.properties:
                if (matching_type := find(ctx.types, lambda k: k.name == parameter.value)) == None:
                    raise TranslationError(f"Trigger parameter {parameter.key} declares a type of {parameter.value} but that type is not known.", parameter.filename, parameter.line)
                params.append(TriggerParameter(parameter.key, parameter.value))

        ## run the type-checker against the trigger expression
        ## the locals table for triggers is just the input params.
        result_type = runTypeCheck(trigger_definition.value, trigger_definition.filename, trigger_definition.line, params, ctx)
        if result_type != trigger_type.name:
            raise TranslationError(f"Trigger with name {trigger_name} declared return type of {trigger_type.name} but resolved type was {result_type}.", trigger_definition.filename, trigger_definition.line)

        ctx.triggers.append(TriggerDefinition(trigger_name, trigger_type.name, None, params, trigger_definition.filename, trigger_definition.line))

def translateStructs(load_ctx: LoadContext, ctx: TranslationContext):
    for struct_definition in load_ctx.struct_definitions:
        ## determine final type name and check if it is already in use.
        type_name = struct_definition.name if struct_definition.namespace == None else f"{struct_definition.namespace}.{struct_definition.name}"
        if (original := find(ctx.types, lambda k: k.name == type_name)) != None:
            raise TranslationError(f"Type with name {type_name} was redefined: original definition at {original.filename}:{original.line}", struct_definition.filename, struct_definition.line)
        
        ## check that all members of the struct are known types
        ## also, sum the total size of the structure.
        struct_size = 0
        struct_members: List[str] = []
        for member_name in struct_definition.members.properties:
            if (member := find(ctx.types, lambda k: k.name == member_name.value)) == None:
                raise TranslationError(f"Member {member_name.key} on structure {type_name} has type {member_name.value}, but this type does not exist.", member_name.filename, member_name.line)
            struct_size += member.size
            struct_members.append(f"{member_name.key}:{member.name}")
        
        ## append this to the type list, in translation context we make no distincition between structures and other types.
        ctx.types.append(TypeDefinition(type_name, TypeCategory.STRUCTURE, struct_size, struct_members, struct_definition.filename, struct_definition.line))

def translateTypes(load_ctx: LoadContext, ctx: TranslationContext):
    for type_definition in load_ctx.type_definitions:
        ## determine final type name and check if it is already in use.
        type_name = type_definition.name if type_definition.namespace == None else f"{type_definition.namespace}.{type_definition.name}"
        if (original := find(ctx.types, lambda k: k.name == type_name)) != None:
            raise TranslationError(f"Type with name {type_name} was redefined: original definition at {original.filename}:{original.line}", type_definition.filename, type_definition.line)

        ## determine the type category and type members
        if type_definition.type.lower() == "alias":
            type_category = TypeCategory.ALIAS
            if (alias := find(type_definition.properties, lambda k: k.key.lower() == "source")) == None:
                raise TranslationError(f"Alias type {type_name} must specify an alias source.", type_definition.filename, type_definition.line)
            if (source := find(ctx.types, lambda k: k.name == alias.value)) == None:
                raise TranslationError(f"Alias type {type_name} references source type {alias.value}, but that type does not exist.", alias.filename, alias.line)
            type_members = [alias.value]
            target_size = source.size
        elif type_definition.type.lower() == "union":
            type_category = TypeCategory.UNION
            type_members: List[str] = []
            target_size = -1
            for property in type_definition.properties:
                if property.key == "member":
                    if (target := find(ctx.types, lambda k: k.name == property.value)) == None:
                        raise TranslationError(f"Union type {type_name} references source type {property.value}, but that type does not exist.", type_definition.filename, type_definition.line)
                    if target_size == -1:
                        target_size = target.size
                    if target.size != target_size:
                        raise TranslationError(f"Union type {type_name} has member size {target_size} but attempted to include type {target.name} with mismatched size {target.size}.", property.filename, property.line)
                    type_members.append(target.name)
            if len(type_members) == 0:
                raise TranslationError(f"Union type {type_name} must specify at least one member.", type_definition.filename, type_definition.line)
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
                raise TranslationError("Flag types may not support more than 32 members.", type_definition.filename, type_definition.line)
            target_size = 32
        else:
            raise TranslationError(f"Unrecognized type category {type_definition.type} in Define Type section.", type_definition.filename, type_definition.line)
        
        ctx.types.append(TypeDefinition(type_name, type_category, target_size, type_members, type_definition.filename, type_definition.line))

def translateContext(load_ctx: LoadContext) -> TranslationContext:
    ctx = TranslationContext(load_ctx.filename)

    ctx.types = builtins.getBaseTypes()
    ctx.triggers = builtins.getBaseTriggers()
    ctx.templates = builtins.getBaseTemplates()

    translateTypes(load_ctx, ctx)
    translateStructs(load_ctx, ctx)
    translateTriggers(load_ctx, ctx)
    translateTemplates(load_ctx, ctx)
    replaceTemplates(load_ctx, ctx)

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
        #print(translated)
    except TranslationError as exc:
        print("Translation terminated with an error.")
        print(f"\t{exc.message}")