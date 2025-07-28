import os

from mtl.utils.func import find, compiler_internal
from mtl.types.shared import TranslationError
from mtl.types.context import LoadContext, TranslationMode
from mtl.types.ini import *
from mtl.parser import ini, trigger

def loadFile(file: str, cycle: list[str]) -> LoadContext:
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

def parseTarget(sections: list[INISection], mode: TranslationMode, ctx: LoadContext):
    ## group sections into states, templates, triggers, types, includes, etc
    index = 0
    while index < len(sections):
        section = sections[index]
        if section.name.lower().startswith("statedef "):
            statedef = StateDefinitionSection(section.name[9:], section.properties, section.location)
            ctx.state_definitions.append(statedef)

            while index + 1 < len(sections) and sections[index + 1].name.lower().startswith("state "):
                properties: list[StateControllerProperty] = []
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
            locals: list[INIProperty] = []
            for prop in section.properties:
                if prop.key == "local":
                    locals.append(prop)
            template.locals = locals

            while index + 1 < len(sections):
                if sections[index + 1].name.lower().startswith("state "):
                    properties: list[StateControllerProperty] = []
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

def processIncludes(cycle: list[str], ctx: LoadContext):
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
        imported_names: list[str] = []
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