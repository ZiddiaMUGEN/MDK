from mtl.types.context import LoadContext, TranslationContext
from mtl.types.translation import *
from mtl.utils.compiler import TranslationError, find_type, unpack_types, find
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
            struct_size += member.size
            struct_members.append(f"{member_name.key}:{member.name}")
        
        ## append this to the type list, in translation context we make no distincition between structures and other types.
        ctx.types.append(TypeDefinition(type_name, TypeCategory.STRUCTURE, struct_size, struct_members, struct_definition.location))
    print(f"Successfully resolved {len(ctx.types)} type and structure definitions")

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