import os

from mtl.types.context import *
from mtl.types.shared import TranslationError, DebuggerError
from mtl.utils.compiler import find_trigger, find_type, find, equals_insensitive, compiler_internal
from mtl.utils.constant import MTL_VERSION, DEBUGGER_VERSION
from mtl.utils.binary import *

def addStringToDatabase(name: str, ctx: TranslationContext):
    if name not in ctx.debugging.strings:
        ctx.debugging.strings.append(name)

def getDefRelativePath(name: str, base: str) -> str:
    def_path = os.path.dirname(os.path.abspath(base))
    rel_path = os.path.relpath(os.path.abspath(name), def_path)
    while rel_path.startswith("..\\") or rel_path.startswith("../"):
        rel_path = rel_path[3:]
    return rel_path

def addPathToDatabase(name: str, ctx: TranslationContext):
    addStringToDatabase(getDefRelativePath(name, ctx.filename), ctx)

def addTypesToDatabase(ctx: TranslationContext):
    ## iterate each type.
    for type in ctx.types:
        info = DebugTypeInfo(type.name, type.category, [], [], type.size, type.location)
        addStringToDatabase(type.name, ctx)
        addPathToDatabase(type.location.filename, ctx)
        for member in type.members:
            if type.category in [TypeCategory.ENUM, TypeCategory.FLAG, TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG]:
                addStringToDatabase(member, ctx)
                info.members.append(member)
            elif type.category in [TypeCategory.STRUCTURE, TypeCategory.BUILTIN_STRUCTURE]:
                components = member.split(":")
                addStringToDatabase(components[0], ctx)
                info.member_names.append(components[0])
                if (target := find_type(components[1], ctx)) == None:
                    raise TranslationError(f"Could not identify type specified by name {components[1]}.", type.location)
                info.members.append(target)
            else:
                ## let this reference the target type.
                if (target := find_type(member, ctx)) == None:
                    raise TranslationError(f"Could not identify type specified by name {member}.", type.location)
                info.members.append(target)
        ctx.debugging.types.append(info)

def addTriggersToDatabase(ctx: TranslationContext):
    for trigger in ctx.triggers:
        info = DebugTriggerInfo(trigger.name, trigger.category, trigger.type, [], [], trigger.exprn, trigger.location)
        addStringToDatabase(trigger.name, ctx)
        addPathToDatabase(trigger.location.filename, ctx)
        for param in trigger.params:
            addStringToDatabase(param.name, ctx)
            info.parameter_names.append(param.name)
            info.parameter_types.append(param.type)
        ctx.debugging.triggers.append(info)

def addTemplatesToDatabase(ctx: TranslationContext):
    for template in ctx.templates:
        info = DebugTemplateInfo(template.name, template.category, [], [], [], [], template.location)
        addStringToDatabase(template.name, ctx)
        addPathToDatabase(template.location.filename, ctx)
        for param in template.params:
            addStringToDatabase(param.name, ctx)
            info.parameter_names.append(param.name)
            info.parameter_types.append(param.type)
        for param in template.locals:
            addStringToDatabase(param.name, ctx)
            info.local_names.append(param.name)
            info.local_types.append(param.type)
        ctx.debugging.templates.append(info)

def addGlobalsToDatabase(ctx: TranslationContext):
    for var in ctx.globals:
        info = DebugParameterInfo(var.name, var.type, var.scope, var.allocations, var.is_system)
        addStringToDatabase(var.name, ctx)
        ctx.debugging.globals.append(info)

def addStateDefinitionsToDatabase(ctx: TranslationContext):
    for statedef in ctx.statedefs:
        addStringToDatabase(statedef.name, ctx)
        addPathToDatabase(statedef.location.filename, ctx)
        state_id = statedef.parameters.id if statedef.parameters.id != None else -4
        info = DebugStateInfo(statedef.name, state_id, statedef.scope, statedef.parameters.is_common, statedef.location, [], [], [])
        for local in statedef.locals:
            local_info = DebugParameterInfo(local.name, local.type, statedef.scope, local.allocations, local.is_system)
            addStringToDatabase(local.name, ctx)
            info.locals.append(local_info)
        for controller in statedef.states:
            addPathToDatabase(controller.location.filename, ctx)
            info.states.append(controller.location)
        for controller in statedef.states:
            addStringToDatabase(controller.name, ctx)
            ctrl_info = DebugControllerInfo(controller.name, [])
            for trigger in controller.properties:
                addReferencedTriggerToDatabase(trigger.value, ctrl_info, ctx)
            for idx in controller.triggers:
                for trigger in controller.triggers[idx].triggers:
                    addReferencedTriggerToDatabase(trigger, ctrl_info, ctx)
            info.state_data.append(ctrl_info)
        ctx.debugging.states.append(info)

def addReferencedTriggerToDatabase(trigger: TriggerTree, info: DebugControllerInfo, ctx: TranslationContext):
    if trigger.node == TriggerTreeNode.ATOM and (resolved := find_trigger(trigger.operator, [], ctx, trigger.location)) != None:
        if resolved.name not in info.triggers:
            info.triggers.append(resolved.name)
    for child in trigger.children:
        addReferencedTriggerToDatabase(child, info, ctx)

def writeDatabase(filename: str, ctx: DebuggingContext):
    with open(filename, mode='wb') as f:
        ## write header
        write_string(MTL_VERSION, f)
        f.seek(16)
        write_integer(DEBUGGER_VERSION, f)
        f.seek(80)

        ## write strings table
        write_integer(len(ctx.strings), f)
        for string in ctx.strings:
            write_string(string, f)

        ## write types table
        write_integer(len(ctx.types), f)
        for type in ctx.types:
            write_integer(ctx.strings.index(type.name), f)
            write_byte(type.category.value, f)
            write_integer(type.size, f)
            write_short(len(type.members), f)
            for index in range(len(type.members)):
                member = type.members[index]
                if isinstance(member, str):
                    write_integer(ctx.strings.index(member), f)
                    if index < len(type.member_names):
                        write_integer(ctx.strings.index(type.member_names[index]), f)
                    else:
                        write_integer(-1, f)
                elif isinstance(member, TypeDefinition):
                    if (target := find(ctx.types, lambda k: equals_insensitive(member.name, k.name))) == None: # type: ignore
                        raise TranslationError(f"Could not find debug info for type definition with name {member.name}.", member.location)
                    write_integer(ctx.types.index(target), f)
                    if index < len(type.member_names):
                        write_integer(ctx.strings.index(type.member_names[index]), f)
                    else:
                        write_integer(-1, f)
            write_integer(ctx.strings.index(getDefRelativePath(type.location.filename, ctx.filename)), f)
            write_integer(type.location.line, f)

        ## write triggers table
        write_integer(len(ctx.triggers), f)
        for trigger in ctx.triggers:
            write_integer(ctx.strings.index(trigger.name), f)
            write_byte(trigger.category.value, f)
            if (target := find(ctx.types, lambda k: equals_insensitive(trigger.returns.name, k.name))) == None:
                raise TranslationError(f"Could not find debug info for type definition with name {trigger.returns.name}.", trigger.location)
            write_integer(ctx.types.index(target), f)
            write_short(len(trigger.parameter_types), f)
            for index in range(len(trigger.parameter_types)):
                if (target := find(ctx.types, lambda k: equals_insensitive(trigger.parameter_types[index].name, k.name))) == None:
                    raise TranslationError(f"Could not find debug info for type definition with name {trigger.parameter_types[index].name}.", trigger.location)
                write_integer(ctx.types.index(target), f)
                write_integer(ctx.strings.index(trigger.parameter_names[index]), f)
            """
            if trigger.expression != None:
                write_tree(trigger.expression, f)
            else:
                write_byte(-2, f)
            """
            write_integer(ctx.strings.index(getDefRelativePath(trigger.location.filename, ctx.filename)), f)
            write_integer(trigger.location.line, f)

        ## write templates table
        write_integer(len(ctx.templates), f)
        for template in ctx.templates:
            write_integer(ctx.strings.index(template.name), f)
            write_byte(template.category.value, f)
            write_short(len(template.parameter_types), f)
            for index in range(len(template.parameter_types)):
                write_byte(len(template.parameter_types[index]), f)
                for param in template.parameter_types[index]:
                    if (target := find(ctx.types, lambda k: equals_insensitive(param.type.name, k.name))) == None: # type: ignore
                        raise TranslationError(f"Could not find debug info for type definition with name {param.type.name}.", template.location) # type: ignore
                    write_integer(ctx.types.index(target), f)
                write_integer(ctx.strings.index(template.parameter_names[index]), f)
            write_short(len(template.local_types), f)
            for index in range(len(template.local_types)):
                if (target := find(ctx.types, lambda k: equals_insensitive(template.local_types[index].name, k.name))) == None:
                    raise TranslationError(f"Could not find debug info for type definition with name {template.local_types[index].name}.", template.location)
                write_integer(ctx.types.index(target), f)
                write_integer(ctx.strings.index(template.local_names[index]), f)
            write_integer(ctx.strings.index(getDefRelativePath(template.location.filename, ctx.filename)), f)
            write_integer(template.location.line, f)

        ## write global variables table
        write_integer(len(ctx.globals), f)
        for var in ctx.globals:
            write_integer(ctx.strings.index(var.name), f)
            if (target := find(ctx.types, lambda k: equals_insensitive(var.type.name, k.name))) == None: # type: ignore
                raise TranslationError(f"Could not find debug info for type definition with name {var.type.name}.", template.location) # type: ignore
            write_integer(ctx.types.index(target), f)
            write_byte(var.scope.type.value, f)
            if var.scope.target != None:
                write_integer(var.scope.target, f)
            else:
                write_integer(-1, f)
            write_short(len(var.allocations), f)
            for allocation in var.allocations:
                write_byte(allocation[0], f)
                write_byte(allocation[1], f)
            write_byte(1 if var.system else 0, f)

        ## write state definitions
        write_integer(len(ctx.states), f)
        for state in ctx.states:
            write_integer(ctx.strings.index(state.name), f)
            write_integer(state.id, f)
            write_byte(state.scope.type.value, f)
            if state.scope.target != None:
                write_integer(state.scope.target, f)
            else:
                write_integer(-1, f)
            write_byte(1 if state.is_common else 0, f)
            write_integer(ctx.strings.index(getDefRelativePath(state.location.filename, ctx.filename)), f)
            write_integer(state.location.line, f)
            write_short(len(state.locals), f)
            for var in state.locals:
                write_integer(ctx.strings.index(var.name), f)
                if (target := find(ctx.types, lambda k: equals_insensitive(var.type.name, k.name))) == None: # type: ignore
                    raise TranslationError(f"Could not find debug info for type definition with name {var.type.name}.", template.location) # type: ignore
                write_integer(ctx.types.index(target), f)
                write_short(len(var.allocations), f)
                for allocation in var.allocations:
                    write_byte(allocation[0], f)
                    write_byte(allocation[1], f)
            write_short(len(state.states), f)
            for controller in state.states:
                write_integer(ctx.strings.index(getDefRelativePath(controller.filename, ctx.filename)), f)
                write_integer(controller.line, f)
            ## because the database spec specifies a new table after the controller locations table for controller triggers,
            ## we need to redo this iteration.
            write_short(len(state.state_data), f)
            for controller in state.state_data:
                write_integer(ctx.strings.index(controller.type), f)
                write_short(len(controller.triggers), f)
                for trigger in controller.triggers:
                    write_integer(ctx.strings.index(trigger), f)

## loads context.
def load(filename: str) -> DebuggingContext:
    ctx = DebuggingContext()
    with open(filename, mode='rb') as f:
        ## read header
        ## there's no need to interpret the MTL header for now.
        f.seek(16)
        if (version := read_integer(f)) > DEBUGGER_VERSION:
            raise DebuggerError(f"Cannot launch debugger: input database has version {version}, which is newer than mtldbg installation version {DEBUGGER_VERSION}.")
        f.seek(80)

        ## read strings
        for _ in range(read_integer(f)):
            ctx.strings.append(read_string(f))
        
        ## read types
        start_index = f.tell()
        for _ in range(read_integer(f)):
            name = ctx.strings[read_integer(f)]
            category = TypeCategory(read_byte(f))
            size = read_integer(f)
            ## for first pass just ignore members, because we need to re-run through for forward
            ## type references anyway.
            for _ in range(read_short(f)):
                f.seek(f.tell() + 8)
            filename = ctx.strings[read_integer(f)]
            line = read_integer(f)
            ctx.types.append(DebugTypeInfo(name, category, [], [], size, Location(filename, line)))

        ## now seek back to the start of the type table and load members.
        f.seek(start_index)
        for index in range(read_integer(f)):
            target = ctx.types[index]
            f.seek(f.tell() + 9)
            for _ in range(read_short(f)):
                member_index = read_integer(f)
                member_name = read_integer(f)
                if target.category in [TypeCategory.ENUM, TypeCategory.FLAG, TypeCategory.STRING_ENUM, TypeCategory.STRING_FLAG]:
                    target.members.append(ctx.strings[member_index])
                else:
                    target.members.append(ctx.types[member_index])
                if member_name != -1:
                    target.member_names.append(ctx.strings[member_name])
            f.seek(f.tell() + 8)

        ## read triggers
        for _ in range(read_integer(f)):
            name = ctx.strings[read_integer(f)]
            category = TriggerCategory(read_byte(f))
            returns = ctx.types[read_integer(f)]
            parameter_types: list[TypeDefinition | DebugTypeInfo] = []
            parameter_names: list[str] = []
            for _ in range(read_short(f)):
                parameter_types.append(ctx.types[read_integer(f)])
                parameter_names.append(ctx.strings[read_integer(f)])
            tree = None #read_tree(f, compiler_internal())
            filename = ctx.strings[read_integer(f)]
            line = read_integer(f)
            ctx.triggers.append(DebugTriggerInfo(name, category, returns, parameter_types, parameter_names, tree, Location(filename, line)))

        ## read templates
        for _ in range(read_integer(f)):
            name = ctx.strings[read_integer(f)]
            category = TemplateCategory(read_byte(f))
            parameter_types: list[list[TypeDefinition] | list[DebugTypeInfo]] = []
            parameter_names: list[str] = []
            for _ in range(read_short(f)):
                specifiers: list[DebugTypeInfo] = []
                for _ in range(read_byte(f)):
                    specifiers.append(ctx.types[read_integer(f)])
                parameter_types.append(specifiers)
                parameter_names.append(ctx.strings[read_integer(f)])
            local_types: list[TypeDefinition | DebugTypeInfo] = []
            local_names: list[str] = []
            for _ in range(read_short(f)):
                local_types.append(ctx.types[read_integer(f)])
                local_names.append(ctx.strings[read_integer(f)])
            filename = ctx.strings[read_integer(f)]
            line = read_integer(f)
            ctx.templates.append(DebugTemplateInfo(name, category, parameter_types, parameter_names, local_types, local_names, Location(filename, line)))
        
        ## read globals
        for _ in range(read_integer(f)):
            name = ctx.strings[read_integer(f)]
            type = ctx.types[read_integer(f)]
            scope = StateScopeType(read_byte(f))
            target = read_integer(f)
            allocations: list[tuple[int, int]] = []
            for _ in range(read_short(f)):
                allocations.append((read_byte(f), read_byte(f)))
            system = True if read_byte(f) == 1 else False
            ctx.globals.append(DebugParameterInfo(name, type, StateDefinitionScope(scope, target if target != -1 else None), allocations, system))

        ## read state definitions
        for _ in range(read_integer(f)):
            name = ctx.strings[read_integer(f)]
            id = read_integer(f)
            scope = StateScopeType(read_byte(f))
            target = read_integer(f)
            is_common = read_byte(f) != 0
            filename = ctx.strings[read_integer(f)]
            line = read_integer(f)
            sds = StateDefinitionScope(scope, target if target != -1 else None)
            locals: list[DebugParameterInfo] = []
            controllers: list[Location] = []
            controller_data: list[DebugControllerInfo] = []
            for _ in range(read_short(f)):
                local_name = ctx.strings[read_integer(f)]
                local_type = ctx.types[read_integer(f)]
                allocations: list[tuple[int, int]] = []
                for _ in range(read_short(f)):
                    allocations.append((read_byte(f), read_byte(f)))
                locals.append(DebugParameterInfo(local_name, local_type, sds, allocations, False))
            for _ in range(read_short(f)):
                controllers.append(Location(ctx.strings[read_integer(f)], read_integer(f)))
            for _ in range(read_short(f)):
                ctrl_type = ctx.strings[read_integer(f)]
                triggers: list[str] = []
                for _ in range(read_short(f)):
                    triggers.append(ctx.strings[read_integer(f)])
                controller_data.append(DebugControllerInfo(ctrl_type, triggers))
            ctx.states.append(DebugStateInfo(name, id, sds, is_common, Location(filename, line), locals, controllers, controller_data))

    return ctx