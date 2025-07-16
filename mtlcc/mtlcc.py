import argparse
import os
from typing import List, Callable, TypeVar

from mtl.parsers import ini, trigger
from mtl.shared import *
from mtl.error import TranslationError
from mtl import builtins

T = TypeVar('T')
def find(l: List[T], p: Callable[[T], bool]) -> Optional[T]:
    result = next(filter(p, l), None)
    return result

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

            if index + 1 >= len(sections) or sections[index + 1].name.lower().startswith("define members"):
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
                imported_names += [property.value.lower()]

        if len(imported_names) != 0:
            include_context.templates = list(filter(lambda k: k.name.lower() in imported_names, include_context.templates))
            include_context.triggers = list(filter(lambda k: k.name.lower() in imported_names, include_context.triggers))
            include_context.type_definitions = list(filter(lambda k: k.name.lower() in imported_names, include_context.type_definitions))
            include_context.struct_definitions = list(filter(lambda k: k.name.lower() in imported_names, include_context.struct_definitions))

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
                raise TranslationError(f"Alias type {type_name} references source type {alias.value}, but that type does not exist.", type_definition.filename, type_definition.line)
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
                        raise TranslationError(f"Union type {type_name} has member size {target_size} but attempted to include type {target.name} with mismatched size {target.size}.", type_definition.filename, type_definition.line)
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

    translateTypes(load_ctx, ctx)

    return ctx

if __name__ == "__main__":
    ## TODO: need a project file. need to be able to parse AIR, SPR, SND and multiple MTL/CNS files.
    parser = argparse.ArgumentParser(prog='mtlcc', description='Translation tool from MTL templates into CNS character code')
    parser.add_argument('input', help='Path to the MTL template to translate')

    args = parser.parse_args()
    ## note: the spec states that translation of included files should stop at step 3.
    ## this is guaranteed by having steps up to 3 in `loadFile`, and remaining steps handled in `translateContext`.
    loadContext = loadFile(args.input, [])
    translated = translateContext(loadContext)
    print(translated)