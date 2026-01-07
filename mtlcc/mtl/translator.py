from mtl.types.context import LoadContext, TranslationContext
from mtl.types.translation import *
from mtl.types.shared import TranslationError, DebugCategory
from mtl.types.builtins import *

from mtl.utils.func import *
from mtl.utils.compiler import *
from mtl.utils.debug import debuginfo
from mtl.utils.constant import MTL_VERSION
from mtl import builtins
from mtl.parser.trigger import parseTrigger

from mtl.debugging import database

from mtl.writer import *

import copy

def translateTypes(load_ctx: LoadContext, ctx: TranslationContext):
    print(f"Start processing type definitions...")
    for type_definition in load_ctx.type_definitions:
        ## determine final type name and check if it is already in use.
        type_name = type_definition.name if type_definition.namespace == None else f"{type_definition.namespace}.{type_definition.name}"
        if (original := find_type(type_name, ctx)) != None:
            raise TranslationError(f"Type with name {type_name} was redefined: original definition at {original.location.filename}:{original.location.line}", type_definition.location)

        ## determine the type category and type members
        if type_definition.type.lower() == "alias":
            ## an alias has one `source` member, which may be 
            type_category = TypeCategory.ALIAS
            if (alias := find(type_definition.properties, lambda k: k.key.lower() == "source")) == None:
                raise TranslationError(f"Alias type {type_name} must specify an alias source.", type_definition.location)
            if (source := unpack_types(alias.value, ctx, alias.location)) == None:
                raise TranslationError(f"Alias type {type_name} references source definition {alias.value}, but the definition could not be resolved.", alias.location)
            type_members = [alias.value]
            target_size = 0
            for s in source:
                target_size += s.type.size
        elif type_definition.type.lower() == "union":
            type_category = TypeCategory.UNION
            type_members: list[str] = []
            target_size = -1
            for property in type_definition.properties:
                if property.key == "member":
                    if (target := find_type(property.value, ctx)) == None:
                        raise TranslationError(f"Union type {type_name} references source type {property.value}, but that type does not exist.", type_definition.location)
                    if target.category == TypeCategory.BUILTIN_DENY:
                        raise TranslationError(f"Union type {type_name} references source type {property.value}, but user-defined unions are not permitted to use that type.", type_definition.location)
                    if target_size == -1:
                        target_size = target.size
                    if target.size != target_size:
                        raise TranslationError(f"Union type {type_name} has member size {target_size} but attempted to include type {target.name} with mismatched size {target.size}.", property.location)
                    type_members.append(target.name)
            if len(type_members) == 0:
                raise TranslationError(f"Union type {type_name} must specify at least one member.", type_definition.location)
        elif type_definition.type.lower() == "enum":
            type_category = TypeCategory.ENUM
            type_members: list[str] = []
            for property in type_definition.properties:
                if property.key == "enum":
                    type_members.append(property.value)
            target_size = 32
        elif type_definition.type.lower() == "flag":
            type_category = TypeCategory.FLAG
            type_members: list[str] = []
            for property in type_definition.properties:
                if property.key == "flag":
                    type_members.append(property.value)
            if len(type_members) > 32:
                raise TranslationError("Flag types may not support more than 32 members.", type_definition.location)
            target_size = 32
        else:
            raise TranslationError(f"Unrecognized type category {type_definition.type} in Define Type section.", type_definition.location)
        
        definition = TypeDefinition(type_name, type_category, target_size, type_members, type_definition.location)
        ctx.types.append(definition)

        ## automatically register equality and assignment for all Enum and Flag user-defined types.
        ## if other operators are required, end users should implement it themselves.
        if definition.category == TypeCategory.ENUM:
            ctx.triggers.append(TriggerDefinition("operator=", BUILTIN_BOOL, builtins.builtin_eq, [TypeParameter("expr1", definition), TypeParameter("expr2", definition)], None, definition.location, "operator=", category = TriggerCategory.OPERATOR))
            ctx.triggers.append(TriggerDefinition("operator!=", BUILTIN_BOOL, builtins.builtin_neq, [TypeParameter("expr1", definition), TypeParameter("expr2", definition)], None, definition.location, "operator!=", category = TriggerCategory.OPERATOR))
            ctx.triggers.append(TriggerDefinition("operator:=", definition, builtins.builtin_assign, [TypeParameter("expr1", definition), TypeParameter("expr2", definition)], None, definition.location, "operator:=", category = TriggerCategory.OPERATOR))
        if definition.category == TypeCategory.FLAG:
            ctx.triggers.append(TriggerDefinition("operator=", BUILTIN_BOOL, builtins.flag_eq, [TypeParameter("expr1", definition), TypeParameter("expr2", definition)], None, definition.location, "operator=", category = TriggerCategory.OPERATOR))
            ctx.triggers.append(TriggerDefinition("operator!=", BUILTIN_BOOL, builtins.flag_neq, [TypeParameter("expr1", definition), TypeParameter("expr2", definition)], None, definition.location, "operator!=", category = TriggerCategory.OPERATOR))
            ctx.triggers.append(TriggerDefinition("operator|", BUILTIN_BOOL, builtins.flag_join, [TypeParameter("expr1", definition), TypeParameter("expr2", definition)], None, definition.location, "operator|", category = TriggerCategory.OPERATOR))
            ctx.triggers.append(TriggerDefinition("operator:=", definition, builtins.builtin_assign, [TypeParameter("expr1", definition), TypeParameter("expr2", definition)], None, definition.location, "operator:=", category = TriggerCategory.OPERATOR))

def translateStructs(load_ctx: LoadContext, ctx: TranslationContext):
    for struct_definition in load_ctx.struct_definitions:
        ## determine final type name and check if it is already in use.
        type_name = struct_definition.name if struct_definition.namespace == None else f"{struct_definition.namespace}.{struct_definition.name}"
        if (original := find_type(type_name, ctx)) != None:
            raise TranslationError(f"Type with name {type_name} was redefined: original definition at {original.location.filename}:{original.location.line}", struct_definition.location)
        
        ## check that all members of the struct are known types
        ## also, sum the total size of the structure.
        struct_size = 0
        struct_members: list[str] = []
        for member_name in struct_definition.members.properties:
            if (member := find_type(member_name.value, ctx)) == None:
                raise TranslationError(f"Member {member_name.key} on structure {type_name} has type {member_name.value}, but this type does not exist.", member_name.location)
            if member.category == TypeCategory.BUILTIN_DENY:
                raise TranslationError(f"Member {member_name.key} on structure {type_name} has type {member_name.value}, but user-defined structures are not permitted to use this type.", member_name.location)
            struct_size += member.size
            struct_members.append(f"{member_name.key}:{member.name}")
        
        ## append this to the type list, in translation context we make no distincition between structures and other types.
        ctx.types.append(TypeDefinition(type_name, TypeCategory.STRUCTURE, struct_size, struct_members, struct_definition.location))
    print(f"Successfully resolved {len(ctx.types)} type and structure definitions")

def translateTriggers(load_ctx: LoadContext, ctx: TranslationContext):
    print("Start loading trigger function definitions...")
    for trigger_definition in load_ctx.triggers:
        trigger_name = trigger_definition.name if trigger_definition.namespace == None else f"{trigger_definition.namespace}.{trigger_definition.name}"
        if (matching_type := find_type(trigger_name, ctx)) != None:
            raise TranslationError(f"Trigger with name {trigger_name} overlaps type name defined at {matching_type.location.filename}:{matching_type.location.line}: type names are reserved for type initialization.", trigger_definition.location)
        
        # identify matches by name, then inspect type signature
        param_types = [param for param in trigger_definition.params.properties] if trigger_definition.params != None else []
        ## need to resolve the types in param_types to a list of types.
        param_defs: list[TypeParameter] = []
        for param in param_types:
            if (t := find_type(param.value, ctx)) == None:
                return None
            if t.category == TypeCategory.BUILTIN_DENY:
                raise TranslationError(f"Trigger with name {trigger_name} has a parameter with type {t.name}, but user-defined triggers are not permitted to use this type.", trigger_definition.location)
            param_defs.append(TypeParameter(param.key, t))
        ## now try to find a matching overload.
        matched = find_trigger(trigger_name, [param.type for param in param_defs], ctx, trigger_definition.location)
        if matched != None:
            raise TranslationError(f"Trigger with name {trigger_name} was redefined: original definition at {matched.location.filename}:{matched.location.line}", trigger_definition.location)

        ## ensure the expected type of the trigger is known
        if (trigger_type := find_type(trigger_definition.type, ctx)) == None:
            raise TranslationError(f"Trigger with name {trigger_name} declares a return type of {trigger_definition.type} but that type is not known.", trigger_definition.location)
        if trigger_type.category == TypeCategory.BUILTIN_DENY:
            raise TranslationError(f"Trigger with name {trigger_name} declares a return type of {trigger_definition.type}, but user-defined triggers are not permitted to use this type.", trigger_definition.location)

        ## run the type-checker against the trigger expression
        ## the locals table for triggers is just the input params.
        result_type = type_check(trigger_definition.value, param_defs, ctx, expected = [TypeSpecifier(BUILTIN_BOOL)], pass_through = True)
        ## trigger returns and trigger expressions are only permitted to have one return type currently.
        ## ensure only one type was returned.
        if result_type == None or len(result_type) != 1:
            raise TranslationError(f"Could not determine the result type for trigger expression.", trigger_definition.location)
        if get_type_match(result_type[0].type, trigger_type, ctx, trigger_definition.location) == None:
            raise TranslationError(f"Could not match type {result_type[0].type.name} to expected type {trigger_type.name} on trigger {trigger_name}.", trigger_definition.location)

        ctx.triggers.append(TriggerDefinition(trigger_name, trigger_type, None, param_defs, trigger_definition.value, trigger_definition.location, trigger_name.lower()))
    print(f"Successfully resolved {len(ctx.triggers)} trigger function definitions")

def translateTemplates(load_ctx: LoadContext, ctx: TranslationContext):
    print("Start loading template definitions...")
    for template_definition in load_ctx.templates:
        ## determine final template name and check if it is already in use.
        template_name = template_definition.name if template_definition.namespace == None else f"{template_definition.namespace}.{template_definition.name}"
        if (original := find_template(template_name, ctx)) != None:
            raise TranslationError(f"Template with name {template_name} was redefined: original definition at {original.location.filename}:{original.location.line}", template_definition.location)
        
        ## determine the type and default value of any local declarations
        template_locals: list[TypeParameter] = []
        for local in template_definition.locals:
            if (local_param := parse_local(local.value, ctx, local.location)) == None:
                raise TranslationError(f"Could not parse local variable for template from expression {local.value}", local.location)
            if local_param.type.category == TypeCategory.BUILTIN_DENY:
                raise TranslationError(f"Template with name {template_name} declares a local {local_param.name} with type {local_param.type.name}, but user-defined templates are not permitted to use this type.", template_definition.location)
            template_locals.append(local_param)

        ## determine the type of any parameter declarations
        template_params: list[TemplateParameter] = []
        if template_definition.params != None:
            for param in template_definition.params.properties:
                if (param_type := find_type(param.value, ctx)) == None:
                    raise TranslationError(f"A template parameter was declared with a type of {param.value} but that type does not exist.", param.location)
                if param_type.category == TypeCategory.BUILTIN_DENY:
                    raise TranslationError(f"Template with name {template_name} declares a parameter with type {param_type.name}, but user-defined templates are not permitted to use this type.", template_definition.location)
                ## user-defined templates can't specify tuples, so provide a single TypeSpecifier here.
                template_params.append(TemplateParameter(param.key, [TypeSpecifier(param_type)]))

        ## analyse all template states. in this stage we just want to confirm variable usage is correct.
        ## type checking will happen later when we have substituted templates into their call sites.
        template_states: list[StateController] = []
        for state in template_definition.states:
            controller = parse_controller(state, ctx)
            if (target_template := find_template(controller.name, ctx)) == None:
                raise TranslationError(f"Could not find any template or builtin controller with name {controller.name}.", controller.location)
            ## to determine if there are any globals in use, we can just call `type_check`
            ## the type checker will throw an error if it does not recognize any symbol.
            for trigger_group in controller.triggers:
                for trigger in controller.triggers[trigger_group].triggers:
                    type_check(trigger, [TypeParameter(t.name, t.type[0].type) for t in template_params] + template_locals, ctx, expected = [TypeSpecifier(BUILTIN_BOOL)], pass_through = True)
            for property in controller.properties:
                target_prop = find(target_template.params, lambda k: equals_insensitive(k.name, property.key))
                type_check(property.value, [TypeParameter(t.name, t.type[0].type) for t in template_params] + template_locals, ctx, expected = target_prop.type if target_prop != None else None, pass_through = True)
            template_states.append(controller)
        
        ctx.templates.append(TemplateDefinition(template_name, template_params, template_locals, template_states, template_definition.location))
    print(f"Successfully resolved {len(ctx.templates)} template definitions")

def translateStateDefinitions(load_ctx: LoadContext, ctx: TranslationContext):
    print("Start state definition processing...")
    ## this does a portion of statedef translation.
    ## essentially it just builds a StateDefinition object from each StateDefinitionSection object.
    ## this makes it easier to do the next tasks (template/trigger replacement).
    for state_definition in load_ctx.state_definitions:
        ## this is a string for the statedef name, but can also be an integer ID.
        state_name = state_definition.name
        ## identify all parameters which can be set on the statedef
        state_params = StateDefinitionParameters()
        state_params.is_common = state_definition.is_common
        state_scope = StateDefinitionScope(StateScopeType.SHARED, None)
        for prop in state_definition.props:
            ## allow-list the props which can be set here to avoid evil behaviour
            if prop.key.lower() in ["type", "movetype", "physics", "anim", "ctrl", "poweradd", "juggle", "facep2", "hitdefpersist", "movehitpersist", "hitcountpersist", "sprpriority", "velset", "id"]:
                setattr(state_params, prop.key.lower(), make_atom(prop.value))
            elif equals_insensitive(prop.key, "scope"):
                state_scope = get_scope(prop.value, prop.location)
        ## if state name is an ID but an ID was provided, throw an error
        if state_params.id != None and (ival := tryparse(state_name, int)) != None and ival != state_params.id:
            raise TranslationError(f"State definition with name {state_name} has a numeric name, but specifies an explicit ID {state_params.id}.", state_definition.location)
        ## if no ID override provided, and the state name is an ID, set it
        if state_params.id == None and (ival := tryparse(state_name, int)) != None:
            state_params.id = ival
        ## identify all local variable declarations, if any exist
        state_locals: list[TypeParameter] = []
        for prop in state_definition.props:
            if prop.key.lower() == "local":
                if (local := parse_local(prop.value, ctx, prop.location)) == None:
                    raise TranslationError(f"Could not parse local variable for statedef from expression {prop.value}", prop.location)
                local.scope = state_scope
                state_locals.append(local)
        ## pull the list of controllers; we do absolutely zero checking or validation at this stage.
        state_controllers: list[StateController] = []
        for state in state_definition.states:
            controller = parse_controller(state, ctx)
            state_controllers.append(controller)

        ctx.statedefs.append(StateDefinition(state_name, state_params, state_locals, state_controllers, state_scope, state_definition.location))
    print(f"Successfully resolved {len(ctx.statedefs)} state definitions")

def replaceTemplates(ctx: TranslationContext, iterations: int = 0):
    if iterations == 0: print("Start applying template replacements in statedefs...")

    replaced = False

    if iterations > 20:
        raise TranslationError("Template replacement failed to complete after 20 iterations.", compiler_internal(ctx.compiler_flags))
    
    ## process each statedef and each controller within the statedefs
    ## if a controller's `type` property references a non-builtin template, remove
    ## that controller from the state list and insert all the controllers from the template.
    ## if no template at all matches, raise an error.
    for statedef in ctx.statedefs:
        index = 0
        while index < len(statedef.states):
            controller = statedef.states[index]
            if (template := find_template(controller.name, ctx)) == None:
                raise TranslationError(f"No template or builtin controller was found to match state controller with name {controller.name}", controller.location)
            ## we only care about DEFINED templates here. BUILTIN templates are for MUGEN/CNS state controller types.
            if template.category == TemplateCategory.DEFINED:
                replaced = True
                ## 1. copy all the locals declared in the template to the locals of the state, with a prefix to ensure they are uniquified.
                local_prefix = f"{generate_random_string(8)}_"
                local_map: dict[str, str] = {}
                for local in template.locals:
                    statedef.locals.append(TypeParameter(f"{local_prefix}{local.name}", local.type, local.default, local.location, scope = statedef.scope))
                    local_map[local.name] = f"{local_prefix}{local.name}"
                ## 2. copy all controllers from the template, updating uses of the locals to use the new prefix.
                ##    also apply a copy of `ignorehitpause` and `persistent` from the call site.
                new_controllers = copy.deepcopy(template.states)
                for new_controller in new_controllers:
                    for local_name in local_map:
                        old_exprn = TriggerTree(TriggerTreeNode.ATOM, local_name, [], new_controller.location)
                        new_exprn = TriggerTree(TriggerTreeNode.ATOM, local_map[local_name], [], new_controller.location)
                        replace_expression(new_controller, old_exprn, new_exprn)
                    if len(ignorehitpause := find_property("ignorehitpause", controller)) == 1:
                        new_controller.properties.append(copy.deepcopy(ignorehitpause[0]))
                    if len(persistent := find_property("persistent", controller)) == 1:
                        new_controller.properties.append(copy.deepcopy(persistent[0]))
                ## 3. replace all uses of parameters with the expression to substitute for that parameter.
                exprn_map: list[StateControllerProperty] = []
                for param in template.params:
                    if len(target_exprn := find_property(param.name, controller)) != 1 and param.required:
                        raise TranslationError(f"No expression was provided for parameter with name {param.name} on template or controller {controller.name}.", controller.location)
                    if target_exprn != None and len(target_exprn) == 1:
                        exprn_map.append(copy.deepcopy(target_exprn[0]))
                for new_controller in new_controllers:
                    for exprn in exprn_map:
                        old_exprn = TriggerTree(TriggerTreeNode.ATOM, exprn.key, [], new_controller.location)
                        replace_expression(new_controller, old_exprn, exprn.value)

                ## 4. combine the triggers on the template call into one or more triggerall statements and insert into each new controller.
                combined_triggers = merge_triggers(controller.triggers, controller.location)
                for new_controller in new_controllers:
                    if 0 not in new_controller.triggers:
                        new_controller.triggers[0] = TriggerGroup([])
                    new_controller.triggers[0].triggers += combined_triggers

                ## 5. remove the call to the template (at `index`) and insert the new controllers into the statedef
                statedef.states = statedef.states[:index] + new_controllers + statedef.states[index+1:]
                index += len(new_controllers)
                
            index += 1

    ## recurse if any replacements were made.
    if replaced:
        replaceTemplates(ctx, iterations + 1)

    if iterations == 0: print("Successfully completed template replacement.")

def createGlobalsTable(ctx: TranslationContext, forwards: list[ForwardParameter]):
    print("Start global variable identification and assignment...")
    ## initialize the scopes list in ctx based on the scopes of each statedef.
    ## the SHARED, PLAYER, HELPER, and TARGET scopes will all exist even if not used.
    ## the HELPER(xx) scopes are created only if they are used.
    ctx.allocations[StateDefinitionScope(StateScopeType.SHARED, None)] = create_table()
    ctx.allocations[StateDefinitionScope(StateScopeType.PLAYER, None)] = create_table()
    ctx.allocations[StateDefinitionScope(StateScopeType.HELPER, None)] = create_table()
    ctx.allocations[StateDefinitionScope(StateScopeType.TARGET, None)] = create_table()
    ## iterate each statedef and create its scope if missing
    for statedef in ctx.statedefs:
        if statedef.scope not in ctx.allocations:
            ctx.allocations[statedef.scope] = create_table()

    global_list: list[TypeParameter] = []

    ## create a global entry for each known/forward-declared global variable.
    for gv in forwards:
        if (target_type := find_type(gv.type, ctx)) == None:
            raise TranslationError(f"Failed to define forward-declared global variable {gv}: no type with name {gv.type}.", compiler_internal(ctx.compiler_flags))
        global_list.append(TypeParameter(gv.name, target_type, None, compiler_internal(ctx.compiler_flags), scope = gv.scope, is_system = gv.is_system))

    ## iterate all translated statedefs and identify global assignments
    for statedef in ctx.statedefs:
        for controller in statedef.states:
            if (target_template := find_template(controller.name, ctx)) == None:
                raise TranslationError(f"Could not find any template or builtin controller with name {controller.name}.", controller.location)
            for group_id in controller.triggers:
                for trigger in controller.triggers[group_id].triggers:
                    global_list += find_globals(trigger, global_list + statedef.locals, statedef.scope, ctx)
            for property in controller.properties:
                global_list += find_globals(property.value, global_list + statedef.locals, statedef.scope, ctx)
            if controller.name.lower() in ["varset", "varadd"]:
                ## detect any properties which set values.
                for property in controller.properties:
                    target_name = property.key.lower().replace(" ", "")
                    ## don't create a global from a local
                    if find(statedef.locals, lambda k: equals_insensitive(target_name, k.name)) != None:
                        continue
                    if target_name.startswith("var(") or target_name.startswith("fvar(") \
                        or target_name.startswith("sysvar(") or target_name.startswith("sysfvar("):
                        raise TranslationError(f"State controller sets indexed variable {target_name} which is not currently supported by MTL.", property.location)
                    if not target_name.startswith("trigger") and not target_name in ["type", "persistent", "ignorehitpause"]:
                        target_prop = find(target_template.params, lambda k: equals_insensitive(k.name, property.key))
                        if (prop_type := type_check(property.value, global_list + statedef.locals, ctx, expected = target_prop.type if target_prop != None else None, scope = statedef.scope)) == None:
                            raise TranslationError(f"Could not identify target type of global {property} from its assignment.", property.location)
                        if len(prop_type) != 1:
                            raise TranslationError(f"Target type of global {property} was a tuple, but globals cannot contain tuples.", property.location)
                        global_list.append(TypeParameter(property.key, prop_type[0].type, location = property.location, scope = statedef.scope))

    ## ensure all assignments for globals use matching types for matching scopes.
    result: list[TypeParameter] = []
    for param in global_list:
        if (exist := find(result, lambda k: equals_insensitive(k.name, param.name))) == None:
            result.append(param)
            continue
        elif not scopes_compatible(param.scope, exist.scope, ctx):
            raise TranslationError(f"Global parameter {param.name} previously defined in scope {exist.scope.type} but redefined in incompatible scope {param.scope.type}.", param.location)
        elif (wider := get_widest_match(exist.type, param.type, ctx, param.location)) == None:
            raise TranslationError(f"Global parameter {param.name} previously defined as {exist.type.name} but redefined as incompatible type {param.type.name}.", param.location)
        exist.type = wider

    ## now generate additional global entries for each sub-scope.
    result_scoped: list[TypeParameter] = []
    ## 1. any globals with SHARED scope need to be copied to HELPER, PLAYER, HELPER(xx) scopes
    for g in list(filter(lambda k: k.scope.type == StateScopeType.SHARED, result)):
        result_scoped.append(g)
        for scope in ctx.allocations:
            if scope.type in [StateScopeType.PLAYER, StateScopeType.HELPER]:
                g_ = copy.deepcopy(g)
                g_.scope = scope
                result_scoped.append(g_)
    ## 2. any globals with HELPER scope need to be copied to HELPER(xx) scopes
    for g in list(filter(lambda k: k.scope.type == StateScopeType.HELPER and k.scope.target == None, result)):
        result_scoped.append(g)
        for scope in ctx.allocations:
            if scope.type == StateScopeType.HELPER and scope.target != None:
                g_ = copy.deepcopy(g)
                g_.scope = scope
                result_scoped.append(g_)
    ## 3. any globals with TARGET, PLAYER, HELPER(xx) scope are good as-is
    for g in list(filter(lambda k: k.scope.type in [StateScopeType.TARGET, StateScopeType.PLAYER] or (k.scope.type == StateScopeType.HELPER and k.scope.target != None), result)):
        result_scoped.append(g)

    ctx.globals = result_scoped
    print("Finish global variable identification.")

def fullPassTypeCheck(ctx: TranslationContext):
    print("Waiting for initial type check to complete...")
    for statedef in ctx.statedefs:
        table = statedef.locals + list(filter(lambda k: scopes_compatible(statedef.scope, k.scope, ctx), ctx.globals))
        for controller in statedef.states:
            if (target_template := find_template(controller.name, ctx)) == None:
                raise TranslationError(f"Could not find any template or builtin controller with name {controller.name}.", controller.location)
            for group_id in controller.triggers:
                for trigger in controller.triggers[group_id].triggers:
                    result_types = type_check(trigger, table, ctx, expected = [TypeSpecifier(BUILTIN_BOOL)], scope = statedef.scope)
                    if result_types == None or len(result_types) != 1:
                        raise TranslationError(f"Target type of trigger expression was a tuple, but trigger expressions must resolve to bool.", trigger.location)
                    ## for CNS compatibility, we allow any integral type to act as `bool` on a trigger.
                    if result_types[0].type != BUILTIN_BOOL and get_widest_match(result_types[0].type, BUILTIN_INT, ctx, trigger.location) != BUILTIN_INT:
                        raise TranslationError(f"Target type of trigger expression was {result_types[0].type.name}, but trigger expressions must resolve to bool or be convertible to bool.", trigger.location)
            for property in controller.properties:
                ## properties are permitted to be tuples. we need to ensure the specifiers match the expectation for this property.
                ## only type-check expected props.
                if (target_prop := find(target_template.params, lambda k: equals_insensitive(k.name, property.key))) != None:
                    if (result_type := type_check(property.value, table, ctx, expected = target_prop.type, scope = statedef.scope)) == None:
                        raise TranslationError(f"Target type of template parameter {property} could not be resolved to a type.", property.location)
                    match_tuple(result_type, target_prop, ctx, property.location)

def replaceTriggers(ctx: TranslationContext, iterations: int = 0):
    if iterations == 0: print("Start applying trigger replacements in statedefs...")

    replaced = False

    if iterations > 20:
        raise TranslationError("Trigger replacement failed to complete after 20 iterations.", compiler_internal(ctx.compiler_flags))
    
    ## monstrous, but i do not know if it is avoidable.
    for statedef in ctx.statedefs:
        table = statedef.locals + list(filter(lambda k: scopes_compatible(statedef.scope, k.scope, ctx), ctx.globals))
        for controller in statedef.states:
            for group_index in controller.triggers:
                for trigger in controller.triggers[group_index].triggers:
                    replaced = replace_triggers(trigger, table, ctx, scope = statedef.scope) or replaced
            for property in controller.properties:
                replaced = replace_triggers(property.value, table, ctx, scope = statedef.scope) or replaced

    ## recurse if any replacements were made.
    if replaced:
        replaceTriggers(ctx, iterations + 1)

    if iterations == 0: print("Successfully completed trigger replacement.")

def replaceStructAssigns(ctx: TranslationContext):
    ## replace any struct assignments with unpacked assignments.
    ## for example, a VarSet with `myVar = Vector2(1, 1)`
    ## should become a Null with two triggers assigning `myVar x := 1` `myVar y := 1`.
    
    ## 2 cases: VarSet with a Struct initializer, or assignment via `:=` with a Struct initializer.
    ### TODO: implement the `:=` assignment option. it's complicated and for now we're only implementing VarSet.
    for statedef in ctx.statedefs:
        for controller in statedef.states:
            if equals_insensitive(controller.name, "VarSet"):
                final_properties: list[StateControllerProperty] = []
                for property in controller.properties:
                    if property.key.lower().startswith("trigger") or includes_insensitive(property.key, ["ignorehitpause", "persistent", "type"]):
                        final_properties.append(property)
                    else:
                        if property.value.node == TriggerTreeNode.FUNCTION_CALL and (struct := find_type(property.value.operator, ctx)) != None \
                           and struct.category in [TypeCategory.BUILTIN_STRUCTURE, TypeCategory.STRUCTURE]:
                            ## replace with Null and add assignment statements for each member.
                            controller.name = "Null"
                            if 1 not in controller.triggers: controller.triggers[1] = TriggerGroup([])
                            for subindex in range(len(struct.members)):
                                member = struct.members[subindex]
                                member_name = member.split(':')[0]
                                controller.triggers[1].triggers += recursive_struct_assign(
                                    TriggerTree(TriggerTreeNode.ATOM, property.key, [], property.location), 
                                    member_name, struct, property.value.children[subindex], property.location, ctx
                                )
                        else:
                            final_properties.append(property)
                controller.properties = final_properties

def assignVariables(ctx: TranslationContext):
    ## assign locations for each global variable.

    ## allocate for every global first
    for global_variable in ctx.globals:
        create_allocation(global_variable, ctx)

    ## for each statedef, assign locations for each local variable.
    ## because these are local allocations, we store a copy of the allocation tables
    ## prior to allocation, and restore them after.
    for statedef in ctx.statedefs:
        allocation_tables = copy.deepcopy(ctx.allocations)
        for local_variable in statedef.locals:
            create_allocation(local_variable, ctx)
        ctx.allocations = allocation_tables

def applyPersist(ctx: TranslationContext):
    ## for each ChangeState or SelfState, find any `persist` statements
    ## and add an extra `triggerall` to copy the persisted variable.
    for statedef in ctx.statedefs:
        for controller in statedef.states:
            if includes_insensitive(controller.name, ["ChangeState", "SelfState"]):
                target = find_property("value", controller)
                if len(target) != 1:
                    raise TranslationError("All ChangeState and SelfState statements must include a value parameter.", controller.location)
                target_node = target[0].value
                if target_node.node == TriggerTreeNode.MULTIVALUE and len(target_node.children) == 1:
                    target_node = target_node.children[0]
                if target_node.node != TriggerTreeNode.ATOM:
                    ## it's permitted for targets to be expressions, but in that case, persist statements are not supported. we can emit a warning.
                    if len(find_property("persist", controller)) != 0:
                        print(f"Warning at {os.path.realpath(target[0].location.filename)}:{target[0].location.line}: ChangeState and SelfState persist statements can only be used if the target state is an atom, not an expression.")
                else:
                    ## get the locals on the target state
                    if (target_statedef := find(ctx.statedefs, lambda k: equals_insensitive(k.name, target_node.operator))) == None:
                        #raise TranslationError(f"Target state {target_node.operator} for changestate from state {statedef.name} does not exist.", target[0].location)
                        ## FOR NOW ignore this
                        ## TODO: revisit when project files/common1.cns are implemented
                        continue
                    target_locals = target_statedef.locals
                    ## create persist mappings
                    for persisted in find_property("persist", controller):
                        ## find the allocation for the persisted variable source
                        in_source = persisted.value
                        if in_source.node == TriggerTreeNode.MULTIVALUE and len(in_source.children) == 1:
                            in_source = in_source.children[0]
                        if in_source.node != TriggerTreeNode.ATOM:
                            raise TranslationError("ChangeState persist parameter must specify a variable name to be persisted, not an expression.", persisted.location)
                        if (var_source := find(statedef.locals, lambda k: equals_insensitive(in_source.operator, k.name))) == None:
                            raise TranslationError(f"ChangeState persist parameter must specify a local variable name to be persisted, not {in_source.operator}.", persisted.location)
                        if var_source.type.category == TypeCategory.STRUCTURE:
                            raise TranslationError("Can't currently persist structure types.", persisted.location)
                        ## get expression representing the source
                        mask_source = mask_variable(var_source.allocations[0][0], var_source.allocations[0][1], var_source.type.size, var_source.type == BUILTIN_FLOAT, var_source.is_system)
                        ## find the allocation for the persisted variable target
                        if (var_target := find(target_locals, lambda k: equals_insensitive(k.name, in_source.operator))) == None:
                            raise TranslationError(f"ChangeState persisted parameter {in_source.operator} must also exist as a local in target state {target_statedef.name}.", persisted.location)
                        mask_target = f"var({var_target.allocations[0][0]})"
                        if var_target.type == BUILTIN_FLOAT: mask_target = f"f{mask_target}"
                        ## mask source expression so it writes to the right part of mask_target
                        mask_source = mask_write(var_target.allocations[0][0], mask_source, var_target.allocations[0][1], var_target.type.size, var_target.type == BUILTIN_FLOAT, var_target.is_system)
                        ## parse the expression to a trigger
                        new_trigger = parseTrigger(f"{mask_target} := ({mask_source})", persisted.location)
                        ## add a triggerall expression for this allocation.
                        if 0 not in controller.triggers: controller.triggers[0] = TriggerGroup([])
                        controller.triggers[0].triggers.append(TriggerTree(
                            TriggerTreeNode.BINARY_OP,
                            "||",
                            [
                                TriggerTree(TriggerTreeNode.FUNCTION_CALL, "cast", [
                                    new_trigger,
                                    TriggerTree(TriggerTreeNode.ATOM, "bool", [], persisted.location)
                                ], persisted.location),
                                TriggerTree(TriggerTreeNode.ATOM, "true", [], persisted.location),
                            ],
                            persisted.location
                        ))
                    ## remove all persist props
                    controller.properties = list(filter(lambda k: not equals_insensitive(k.key, "persist"), controller.properties))

def applyStateNumbers(ctx: TranslationContext):
    ## assigns unused state numbers to each state definition lacking one.
    ## first identify all state numbers in use.
    all_stateno: set[int] = set()
    for statedef in ctx.statedefs:
        if statedef.parameters.id != None:
            all_stateno.add(statedef.parameters.id)
    ## now assign state numbers sequentially to states missing them.
    for statedef in ctx.statedefs:
        if statedef.parameters.id == None:
            statedef.parameters.id = 0
            if len(all_stateno) == 1: statedef.parameters.id = max(all_stateno) + 1
            if len(all_stateno) > 1: statedef.parameters.id = min(set(range(max(all_stateno) + 2)) - all_stateno)
            all_stateno.add(statedef.parameters.id)

def checkScopes(ctx: TranslationContext):
    ## find any incompatible scopes between source and target on state transitions.
    ## on ChangeState: scopes must be compatible.
    ## on SelfState: scopes must be compatible, UNLESS the source is TARGET, in which case SelfState is always legal.
    ## on Helper: scope of `stateno` must be Shared, Helper, or Helper(xy) where `xy` is the helper ID
    ## on TargetState: scope must be TARGET
    ## on HitDef: p1stateno must be PLAYER or SHARED, p2stateno must be TARGET
    ## on HitOverride: stateno must be compatible
    for statedef in ctx.statedefs:
        for controller in statedef.states:
            if equals_insensitive(controller.name, "ChangeState"):
                target = find_property("value", controller)
                if len(target) != 1:
                    raise TranslationError("All ChangeState and SelfState statements must include a value parameter.", controller.location)
                target_node = target[0].value
                if target_node.node == TriggerTreeNode.MULTIVALUE and len(target_node.children) == 1:
                    target_node = target_node.children[0]
                if target_node.node != TriggerTreeNode.ATOM:
                    if ctx.compiler_flags.no_changestate_expression:
                        raise TranslationError("Cannot validate statedef scope correctness if target of ChangeState is an expression.", target[0].location)
                    ## it's permitted for targets to be expressions, but in that case, we cannot check scopes.
                    print(f"Warning at {os.path.realpath(target[0].location.filename)}:{target[0].location.line}: Cannot validate statedef scope correctness if target of ChangeState is an expression.")
                else:
                    ## check the scopes are compatible.
                    if (target_statedef := find(ctx.statedefs, lambda k: equals_insensitive(k.name, target_node.operator))) != None:
                        state_id = statedef.parameters.id if statedef.parameters.id != None else 0
                        if not scopes_compatible(statedef.scope, target_statedef.scope, ctx) and state_id >= 0:
                            raise TranslationError(f"Target state {target_node.operator} for ChangeState from state {statedef.name} does not have a compatible statedef scope.", target[0].location)
            elif equals_insensitive(controller.name, "SelfState"):
                if statedef.scope.type == StateScopeType.TARGET: continue
                target = find_property("value", controller)
                if len(target) != 1:
                    raise TranslationError("All ChangeState and SelfState statements must include a value parameter.", controller.location)
                target_node = target[0].value
                if target_node.node == TriggerTreeNode.MULTIVALUE and len(target_node.children) == 1:
                    target_node = target_node.children[0]
                if target_node.node != TriggerTreeNode.ATOM:
                    if ctx.compiler_flags.no_changestate_expression:
                        raise TranslationError("Cannot validate statedef scope correctness if target of SelfState is an expression.", target[0].location)
                    ## it's permitted for targets to be expressions, but in that case, we cannot check scopes.
                    print(f"Warning at {os.path.realpath(target[0].location.filename)}:{target[0].location.line}: Cannot validate statedef scope correctness if target of SelfState is an expression.")
                else:
                    ## check the scopes are compatible.
                    if (target_statedef := find(ctx.statedefs, lambda k: equals_insensitive(k.name, target_node.operator))) != None:
                        state_id = statedef.parameters.id if statedef.parameters.id != None else 0
                        if not scopes_compatible(statedef.scope, target_statedef.scope, ctx) and state_id >= 0:
                            raise TranslationError(f"Target state {target_node.operator} for SelfState from state {statedef.name} does not have a compatible statedef scope.", target[0].location)
            elif equals_insensitive(controller.name, "Helper"):
                target = find_property("stateno", controller)
                if len(target) != 1:
                    raise TranslationError("All Helper statements must include a stateno parameter.", controller.location)
                target_node = target[0].value
                if target_node.node == TriggerTreeNode.MULTIVALUE and len(target_node.children) == 1:
                    target_node = target_node.children[0]
                if target_node.node != TriggerTreeNode.ATOM:
                    if ctx.compiler_flags.no_changestate_expression:
                        raise TranslationError("Cannot validate statedef scope correctness if target of Helper stateno is an expression.", target[0].location)
                    ## it's permitted for targets to be expressions, but in that case, we cannot check scopes.
                    print(f"Warning at {os.path.realpath(target[0].location.filename)}:{target[0].location.line}: Cannot validate statedef scope correctness if target of Helper stateno is an expression.")
                else:
                    ## check the scopes are compatible.
                    if (target_statedef := find(ctx.statedefs, lambda k: equals_insensitive(k.name, target_node.operator))) != None:
                        if not target_statedef.scope.type in [StateScopeType.HELPER, StateScopeType.SHARED]:
                            raise TranslationError(f"Target state {target_node.operator} for Helper controller does not have a compatible statedef scope.", target[0].location)
                        if target_statedef.scope.type == StateScopeType.HELPER and target_statedef.scope.target != None:
                            helper_id = find_property("id", controller)
                            if len(helper_id) != 1:
                                raise TranslationError("All Helper statements must include an ID parameter.", controller.location)
                            helper_node = helper_id[0].value
                            if helper_node.node == TriggerTreeNode.MULTIVALUE and len(helper_node.children) == 1:
                                helper_node = helper_node.children[0]
                            if helper_node.node != TriggerTreeNode.ATOM:
                                ## it's permitted for targets to be expressions, but in that case, we cannot check scopes.
                                raise TranslationError(f"Target of Helper controller has scope with ID {target_statedef.scope.target}, but Helper's ID parameter cannot be resolved to a single ID.", helper_node.location)
                            if helper_node.operator != str(target_statedef.scope.target):
                                raise TranslationError(f"Target of Helper controller has scope with ID {target_statedef.scope.target}, but Helper's ID is {helper_node.operator}.", helper_node.location)
            elif equals_insensitive(controller.name, "TargetState"):
                target = find_property("value", controller)
                if len(target) != 1:
                    raise TranslationError("All TargetState statements must include a value parameter.", controller.location)
                target_node = target[0].value
                if target_node.node == TriggerTreeNode.MULTIVALUE and len(target_node.children) == 1:
                    target_node = target_node.children[0]
                if target_node.node != TriggerTreeNode.ATOM:
                    if ctx.compiler_flags.no_changestate_expression:
                        raise TranslationError("Cannot validate statedef scope correctness if target of TargetState is an expression.", target[0].location)
                    ## it's permitted for targets to be expressions, but in that case, we cannot check scopes.
                    print(f"Warning at {os.path.realpath(target[0].location.filename)}:{target[0].location.line}: Cannot validate statedef scope correctness if target of TargetState is an expression.")
                else:
                    ## check the scopes are compatible.
                    if (target_statedef := find(ctx.statedefs, lambda k: equals_insensitive(k.name, target_node.operator))) != None:
                        if target_statedef.scope.type != StateScopeType.TARGET:
                            raise TranslationError(f"Target state {target_node.operator} for TargetState from state {statedef.name} does not have the TARGET scope type.", target[0].location)
            elif equals_insensitive(controller.name, "HitDef"):
                target = find_property("p1stateno", controller)
                if len(target) == 1:
                    target_node = target[0].value
                    if target_node.node == TriggerTreeNode.MULTIVALUE and len(target_node.children) == 1:
                        target_node = target_node.children[0]
                    if target_node.node != TriggerTreeNode.ATOM:
                        if ctx.compiler_flags.no_changestate_expression:
                            raise TranslationError("Cannot validate statedef scope correctness if p1stateno on HitDef is an expression.", target[0].location)
                        ## it's permitted for targets to be expressions, but in that case, we cannot check scopes.
                        print(f"Warning at {os.path.realpath(target[0].location.filename)}:{target[0].location.line}: Cannot validate statedef scope correctness if p1stateno on HitDef is an expression.")
                    else:
                        ## check the scopes are compatible.
                        if (target_statedef := find(ctx.statedefs, lambda k: equals_insensitive(k.name, target_node.operator))) != None:
                            if not scopes_compatible(statedef.scope, target_statedef.scope, ctx):
                                raise TranslationError(f"Target state {target_node.operator} for p1stateno on HitDef from state {statedef.name} does not have a compatible statedef scope.", target[0].location)
                target = find_property("p2stateno", controller)
                if len(target) == 1:
                    target_node = target[0].value
                    if target_node.node == TriggerTreeNode.MULTIVALUE and len(target_node.children) == 1:
                        target_node = target_node.children[0]
                    if target_node.node != TriggerTreeNode.ATOM:
                        if ctx.compiler_flags.no_changestate_expression:
                            raise TranslationError("Cannot validate statedef scope correctness if p2stateno on HitDef is an expression.", target[0].location)
                        ## it's permitted for targets to be expressions, but in that case, we cannot check scopes.
                        print(f"Warning at {os.path.realpath(target[0].location.filename)}:{target[0].location.line}: Cannot validate statedef scope correctness if p2stateno on HitDef is an expression.")
                    else:
                        ## check the scopes are compatible.
                        if (target_statedef := find(ctx.statedefs, lambda k: equals_insensitive(k.name, target_node.operator))) != None:
                            if target_statedef.scope.type != StateScopeType.TARGET:
                                raise TranslationError(f"Target state {target_node.operator} for p2stateno on HitDef from state {statedef.name} does not have the TARGET scope type.", target[0].location)
            elif equals_insensitive(controller.name, "HitOverride"):
                target = find_property("stateno", controller)
                if len(target) != 1:
                    #raise TranslationError("All HitOverride statements must include a stateno parameter.", controller.location)
                    ## note to future self: Elecbyte doc lists `stateno` as required, but it is not really. (see KFM)
                    continue
                target_node = target[0].value
                if target_node.node == TriggerTreeNode.MULTIVALUE and len(target_node.children) == 1:
                    target_node = target_node.children[0]
                if target_node.node != TriggerTreeNode.ATOM:
                    if ctx.compiler_flags.no_changestate_expression:
                        raise TranslationError("Cannot validate statedef scope correctness if target of HitOverride is an expression.", target[0].location)
                    ## it's permitted for targets to be expressions, but in that case, we cannot check scopes.
                    print(f"Warning at {os.path.realpath(target[0].location.filename)}:{target[0].location.line}: Cannot validate statedef scope correctness if target of HitOverride is an expression.")
                else:
                    ## check the scopes are compatible.
                    if (target_statedef := find(ctx.statedefs, lambda k: equals_insensitive(k.name, target_node.operator))) != None:
                        if not scopes_compatible(statedef.scope, target_statedef.scope, ctx):
                            raise TranslationError(f"Target state {target_node.operator} for HitOverride from state {statedef.name} does not have a compatible statedef scope.", target[0].location)
                    
def checkStateLength(ctx: TranslationContext):
    print("Start state length check...")
    for statedef in ctx.statedefs:
        if len(statedef.states) > 512:
            raise TranslationError(f"State definition for state {statedef.name} has more than 512 state controllers after template resolution. Reduce the size of this state definition or its templates.", statedef.location)
    print("Finished state length check.")

def translateContext(load_ctx: LoadContext) -> TranslationContext:
    ctx = TranslationContext(load_ctx.filename, load_ctx.compiler_flags)

    ctx.types = builtins.getBaseTypes()
    ctx.triggers = builtins.getBaseTriggers()
    ctx.templates = builtins.getBaseTemplates()

    if ctx.compiler_flags.no_numeric:
        ctx.types.remove(BUILTIN_NUMERIC)

    translateTypes(load_ctx, ctx)
    translateStructs(load_ctx, ctx)
    database.addTypesToDatabase(ctx)

    translateTriggers(load_ctx, ctx)
    database.addTriggersToDatabase(ctx)
    
    translateTemplates(load_ctx, ctx)

    ## add the default parameters ignorehitpause and persistent to all template definitions.
    for template in ctx.templates:
        template.params.append(TemplateParameter("ignorehitpause", [TypeSpecifier(BUILTIN_BOOL)], False))
        template.params.append(TemplateParameter("persistent", [TypeSpecifier(BUILTIN_INT)], False))

    database.addTemplatesToDatabase(ctx)

    translateStateDefinitions(load_ctx, ctx)
    replaceTemplates(ctx)

    checkStateLength(ctx)
        
    createGlobalsTable(ctx, load_ctx.global_forwards)
    fullPassTypeCheck(ctx)
    replaceTriggers(ctx)
    replaceStructAssigns(ctx)
    checkScopes(ctx)

    assignVariables(ctx)
    database.addGlobalsToDatabase(ctx)

    applyPersist(ctx)
    applyStateNumbers(ctx)
    database.addStateDefinitionsToDatabase(ctx)

    return ctx

def createOutput(ctx: TranslationContext) -> list[str]:
    output: list[str] = []

    ## start by writing a whole heap of debuginfo to the start of the output file.
    ## the debuginfo documents the MTL version in use and the variable table state.
    ## it also documents a list of types, templates, and triggers used during compilation.
    ## this info is not for human consumption, it's used for debugging.
    output += debuginfo(DebugCategory.VERSION_HEADER, MTL_VERSION, ctx.compiler_flags)
    output.append("")

    output += write_type_table(ctx)
    output += write_variable_table(ctx)

    ## now iterate each statedef and produce output, attaching variable debuginfo as needed.
    for statedef in ctx.statedefs:
        matches = [sd for sd in ctx.statedefs if sd.parameters.id == statedef.parameters.id and sd.location != statedef.location]
        #matches = get_all(ctx.statedefs, lambda k: k.parameters.id == statedef.parameters.id and k.location != statedef.location)

        if len(matches) == 0:
            output += write_statedef(statedef, ctx)
        elif len(matches) == 1 and (not statedef.parameters.is_common) and matches[0].parameters.is_common:
            output += write_statedef(statedef, ctx)
        elif len(matches) == 1 and statedef.parameters.is_common:
            continue
        else:
            raise TranslationError(f"State for {statedef.name} with ID {statedef.parameters.id} was redefined: original definition at {matches[0].location.filename}:{matches[0].location.line}", statedef.location)

    return output