import argparse
from typing import List, Callable, TypeVar

from mtl.parsers import ini, trigger
from mtl.shared import *
from mtl.error import TranslationError

T = TypeVar('T')
def find(l: List[T], p: Callable[[T], bool]) -> Optional[T]:
    result = next(filter(p, l), None)
    return result

def parseTarget(sections: List[INISection], mode: TranslationMode, ctx: TranslationContext):
    ## group sections into states, templates, triggers, types, includes, etc
    index = 0
    while index < len(sections):
        section = sections[index]
        if section.name.lower().startswith("statedef "):
            statedef = StateDefinitionSection(section.name[9:], section.properties)
            ctx.state_definitions.append(statedef)

            while index + 1 < len(sections) and sections[index + 1].name.lower().startswith("state "):
                properties: List[StateControllerProperty] = []
                for property in sections[index + 1].properties:
                    properties.append(StateControllerProperty(property.key, trigger.parseTrigger(property.value, property.filename, property.line)))
                statedef.states.append(StateControllerSection(properties))
                index += 1
        elif section.name.lower().startswith("include"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Include sections.", section.filename, section.line)
            ctx.includes.append(section)
        elif section.name.lower().startswith("define type"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.filename, section.line)
            ctx.type_definitions.append(section)
        elif section.name.lower().startswith("define template"):
            if mode == TranslationMode.CNS_MODE:
                raise TranslationError("A CNS file cannot contain MTL Define sections.", section.filename, section.line)
            
            if (prop := find(section.properties, lambda k: k.key.lower() == "name")) == None:
                raise TranslationError("Define Template section must provide a name property.", section.filename, section.line)
            
            template = TemplateSection(prop.value)
            ctx.templates.append(template)

            while index + 1 < len(sections):
                if sections[index + 1].name.lower().startswith("state "):
                    properties: List[StateControllerProperty] = []
                    for property in sections[index + 1].properties:
                        properties.append(StateControllerProperty(property.key, trigger.parseTrigger(property.value, property.filename, property.line)))
                    template.states.append(StateControllerSection(properties))
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

            trigger_section = TriggerSection(name.value, type.value, value.value)
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

            structure = StructureDefinitionSection(prop.value, sections[index + 1])
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

def translateFile(file: str, cycle: List[str]):
    ctx = TranslationContext(file)

    with open(file) as f:
        contents = ini.parse(f.read(), ctx.ini_context)

    mode = TranslationMode.MTL_MODE if file.endswith(".mtl") or file.endswith(".inc") else TranslationMode.CNS_MODE
    parseTarget(contents, mode, ctx)

if __name__ == "__main__":
    ## TODO: need a project file. need to be able to parse AIR, SPR, SND and multiple MTL/CNS files.
    parser = argparse.ArgumentParser(prog='mtlcc', description='Translation tool from MTL templates into CNS character code')
    parser.add_argument('input', help='Path to the MTL template to translate')

    args = parser.parse_args()
    translateFile(args.input, [])