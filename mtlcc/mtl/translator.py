from mtl.types.context import LoadContext, TranslationContext
from mtl.types.translation import *
from mtl.types.shared import TranslationError
from mtl.types.builtins import *

from mtl.utils.func import *
from mtl.utils.compiler import *
from mtl import builtins

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
        
        ctx.types.append(TypeDefinition(type_name, type_category, target_size, type_members, type_definition.location))

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
        result_type = type_check(trigger_definition.value, param_defs, ctx, expected = [TypeSpecifier(BUILTIN_BOOL)])
        ## trigger returns and trigger expressions are only permitted to have one return type currently.
        ## ensure only one type was returned.
        if result_type == None or len(result_type) != 1:
            raise TranslationError(f"Could not determine the result type for trigger expression.", trigger_definition.location)
        if get_type_match(result_type[0].type, trigger_type, ctx, trigger_definition.location) == None:
            raise TranslationError(f"Could not match type {result_type[0].type.name} to expected type {trigger_type.name} on trigger {trigger_name}.", trigger_definition.location)

        ctx.triggers.append(TriggerDefinition(trigger_name, trigger_type, None, param_defs, trigger_definition.value, trigger_definition.location))
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
                    type_check(trigger, [TypeParameter(t.name, t.type[0].type) for t in template_params] + template_locals, ctx, expected = [TypeSpecifier(BUILTIN_BOOL)])
            for property in controller.properties:
                target_prop = find(target_template.params, lambda k: equals_insensitive(k.name, property))
                type_check(controller.properties[property], [TypeParameter(t.name, t.type[0].type) for t in template_params] + template_locals, ctx, expected = target_prop.type if target_prop != None else None)
            template_states.append(controller)
        
        ctx.templates.append(TemplateDefinition(template_name, template_params, template_locals, template_states, template_definition.location))
    print(f"Successfully resolved {len(ctx.templates)} template definitions")

def translateStateDefinitions(load_ctx: LoadContext, ctx: TranslationContext):
    print("Start state definition processing...")
    ## this does a portion of statedef translation.
    ## essentially it just builds a StateDefinition object from each StateDefinitionSection object.
    ## this makes it easier to do the next tasks (template/trigger replacement).
    for state_definition in load_ctx.state_definitions:
        ## in current MTL state_name is just the state ID.
        state_name = state_definition.name
        ## identify all parameters which can be set on the statedef
        state_params = StateDefinitionParameters()
        for prop in state_definition.props:
            ## allow-list the props which can be set here to avoid evil behaviour
            if prop.key.lower() in ["type", "movetype", "physics", "anim", "ctrl", "poweradd", "juggle", "facep2", "hitdefpersist", "movehitpersist", "hitcountpersist", "sprpriority"]:
                setattr(state_params, prop.key.lower(), make_atom(prop.value))
        ## identify all local variable declarations, if any exist
        state_locals: list[TypeParameter] = []
        for prop in state_definition.props:
            if prop.key.lower() == "local":
                if (local := parse_local(prop.value, ctx, prop.location)) == None:
                    raise TranslationError(f"Could not parse local variable for statedef from expression {prop.value}", prop.location)
                state_locals.append(local)
        ## pull the list of controllers; we do absolutely zero checking or validation at this stage.
        state_controllers: list[StateController] = []
        for state in state_definition.states:
            controller = parse_controller(state, ctx)
            state_controllers.append(controller)

        ctx.statedefs.append(StateDefinition(state_name, state_params, state_locals, state_controllers, state_definition.location))
    print(f"Successfully resolved {len(ctx.statedefs)} state definitions")

def replaceTemplates(ctx: TranslationContext, iterations: int = 0):
    if iterations == 0: print("Start applying template replacements in statedefs...")

    replaced = False

    if iterations > 20:
        raise TranslationError("Template replacement failed to complete after 20 iterations.", compiler_internal())
    
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
                    statedef.locals.append(TypeParameter(f"{local_prefix}{local.name}", local.type, local.default, local.location))
                    local_map[local.name] = f"{local_prefix}{local.name}"
                ## 2. copy all controllers from the template, updating uses of the locals to use the new prefix.
                new_controllers = copy.deepcopy(template.states)
                for new_controller in new_controllers:
                    for local_name in local_map:
                        old_exprn = TriggerTree(TriggerTreeNode.ATOM, local_name, [], new_controller.location)
                        new_exprn = TriggerTree(TriggerTreeNode.ATOM, local_map[local_name], [], new_controller.location)
                        replace_expression(new_controller, old_exprn, new_exprn)
                ## 3. replace all uses of parameters with the expression to substitute for that parameter.
                exprn_map: dict[str, TriggerTree] = {}
                for param in template.params:
                    target_exprn = controller.properties[param.name] if param.name in controller.properties else None
                    if target_exprn == None and param.required:
                        raise TranslationError(f"No expression was provided for parameter with name {param.name} on template or controller {controller.name}.", controller.location)
                    if target_exprn != None:
                        exprn_map[param.name] = copy.deepcopy(target_exprn)
                for new_controller in new_controllers:
                    for exprn_name in exprn_map:
                        old_exprn = TriggerTree(TriggerTreeNode.ATOM, exprn_name, [], new_controller.location)
                        replace_expression(new_controller, old_exprn, exprn_map[exprn_name])

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

def createGlobalsTable(ctx: TranslationContext):
    ## iterate all translated statedefs and identify global assignments
    global_list: list[TypeParameter] = []
    for statedef in ctx.statedefs:
        for controller in statedef.states:
            if (target_template := find_template(controller.name, ctx)) == None:
                raise TranslationError(f"Could not find any template or builtin controller with name {controller.name}.", controller.location)
            for group_id in controller.triggers:
                for trigger in controller.triggers[group_id].triggers:
                    global_list += find_globals(trigger, statedef.locals, ctx)
            for property in controller.properties:
                global_list += find_globals(controller.properties[property], statedef.locals, ctx)
            if controller.name.lower() in ["varset", "varadd"]:
                ## detect any properties which set values.
                for property in controller.properties:
                    target_name = property.lower().replace(" ", "")
                    if target_name.startswith("var(") or target_name.startswith("fvar(") \
                        or target_name.startswith("sysvar(") or target_name.startswith("sysfvar("):
                        raise TranslationError(f"State controller sets indexed variable {target_name} which is not currently supported by MTL.", controller.properties[property].location)
                    if not target_name.startswith("trigger") and not target_name in ["type", "persistent", "ignorehitpause"]:
                        target_prop = find(target_template.params, lambda k: equals_insensitive(k.name, property))
                        if (prop_type := type_check(controller.properties[property], statedef.locals, ctx, expected = target_prop.type if target_prop != None else None)) == None:
                            raise TranslationError(f"Could not identify target type of global {property} from its assignment.", controller.properties[property].location)
                        if len(prop_type) != 1:
                            raise TranslationError(f"Target type of global {property} was a tuple, but globals cannot contain tuples.", controller.properties[property].location)
                        global_list.append(TypeParameter(property, prop_type[0].type, location = controller.properties[property].location))

    ## ensure all assignments for globals use matching types.
    result: list[TypeParameter] = []
    for param in global_list:
        if (exist := find(result, lambda k: equals_insensitive(k.name, param.name))) == None:
            result.append(param)
            continue
        elif (wider := get_widest_match(exist.type, param.type, ctx, param.location)) == None:
            raise TranslationError(f"Global parameter {param.name} previously defined as {exist.type.name} but redefined as incompatible type {param.type.name}.", param.location)
        exist.type = wider

    ctx.globals = result

def fullPassTypeCheck(ctx: TranslationContext):
    for statedef in ctx.statedefs:
        table = statedef.locals + ctx.globals
        for controller in statedef.states:
            if (target_template := find_template(controller.name, ctx)) == None:
                raise TranslationError(f"Could not find any template or builtin controller with name {controller.name}.", controller.location)
            for group_id in controller.triggers:
                for trigger in controller.triggers[group_id].triggers:
                    result_types = type_check(trigger, table, ctx, expected = [TypeSpecifier(BUILTIN_BOOL)])
                    if result_types == None or len(result_types) != 1:
                        raise TranslationError(f"Target type of trigger expression was a tuple, but trigger expressions must resolve to bool.", trigger.location)
                    ## for CNS compatibility, we allow any integral type to act as `bool` on a trigger.
                    if get_widest_match(result_types[0].type, BUILTIN_INT, ctx, trigger.location) != BUILTIN_INT:
                        raise TranslationError(f"Target type of trigger expression was {result_types[0].type.name}, but trigger expressions must resolve to bool or be convertible to bool.", trigger.location)
            for property in controller.properties:
                ## properties are permitted to be tuples. we need to ensure the specifiers match the expectation for this property.
                ## only type-check expected props.
                if (target_prop := find(target_template.params, lambda k: equals_insensitive(k.name, property))) != None:
                    if (result_type := type_check(controller.properties[property], table, ctx, expected = target_prop.type)) == None:
                        raise TranslationError(f"Target type of template parameter {property} could not be resolved to a type.", controller.properties[property].location)
                    match_tuple(result_type, target_prop, ctx, controller.properties[property].location)

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
        template.params.append(TemplateParameter("ignorehitpause", [TypeSpecifier(BUILTIN_BOOL)], False))
        template.params.append(TemplateParameter("persistent", [TypeSpecifier(BUILTIN_INT)], False))

    translateStateDefinitions(load_ctx, ctx)
    replaceTemplates(ctx)

    for statedef in ctx.statedefs:
        if len(statedef.states) > 512:
            raise TranslationError(f"State definition for state {statedef.name} has more than 512 state controllers after template resolution. Reduce the size of this state definition or its templates.", statedef.location)
        
    createGlobalsTable(ctx)
    fullPassTypeCheck(ctx)
    replaceTriggers(ctx)

    return ctx