from mtl.types.context import LoadContext, TranslationContext
from mtl.types.translation import *
from mtl.types.shared import TranslationError

from mtl.utils.compiler import find_type, find_trigger, find_template, unpack_types, find, get_type_match, parse_local, parse_controller
from mtl.utils.checker import type_check
from mtl import builtins

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
        matched = find_trigger(trigger_name, [param.type for param in param_defs], ctx)
        if matched != None:
            raise TranslationError(f"Trigger with name {trigger_name} was redefined: original definition at {matched.location.filename}:{matched.location.line}", trigger_definition.location)

        ## ensure the expected type of the trigger is known
        if (trigger_type := find_type(trigger_definition.type, ctx)) == None:
            raise TranslationError(f"Trigger with name {trigger_name} declares a return type of {trigger_definition.type} but that type is not known.", trigger_definition.location)
        if trigger_type.category == TypeCategory.BUILTIN_DENY:
            raise TranslationError(f"Trigger with name {trigger_name} declares a return type of {trigger_definition.type}, but user-defined triggers are not permitted to use this type.", trigger_definition.location)

        ## run the type-checker against the trigger expression
        ## the locals table for triggers is just the input params.
        result_type = type_check(trigger_definition.value, param_defs, ctx)
        ## trigger returns and trigger expressions are only permitted to have one return type currently.
        ## ensure only one type was returned.
        if result_type == None or len(result_type) != 1:
            raise TranslationError(f"Could not determine the result type for trigger expression.", trigger_definition.location)
        if not get_type_match(result_type[0].type, trigger_type, ctx):
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
            ## to determine if there are any globals in use, we can just call `type_check`
            ## the type checker will throw an error if it does not recognize any symbol.
            for trigger_group in controller.triggers:
                for trigger in controller.triggers[trigger_group].triggers:
                    type_check(trigger, [TypeParameter(t.name, t.type[0].type) for t in template_params] + template_locals, ctx)
            for property in controller.properties:
                type_check(controller.properties[property], [TypeParameter(t.name, t.type[0].type) for t in template_params] + template_locals, ctx)
            template_states.append(controller)
        
        ctx.templates.append(TemplateDefinition(template_name, template_params, template_locals, template_states, template_definition.location))
    print(f"Successfully resolved {len(ctx.templates)} template definitions")

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
        template.params.append(TemplateParameter("ignorehitpause", [TypeSpecifier(builtins.BUILTIN_BOOL)], False))
        template.params.append(TemplateParameter("persistent", [TypeSpecifier(builtins.BUILTIN_INT)], False))

    preTranslateStateDefinitions(load_ctx, ctx)
    replaceTemplates(ctx)

    for statedef in ctx.statedefs:
        if len(statedef.states) > 512:
            raise TranslationError(f"State definition for state {statedef.name} has more than 512 state controllers after template resolution. Reduce the size of this state definition or its templates.", statedef.location)
        
    createGlobalsTable(ctx)
    replaceTriggers(ctx)

    return ctx