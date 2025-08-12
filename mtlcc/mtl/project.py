from mtl.types.shared import TranslationError, Location
from mtl.types.ini import INIParserContext
from mtl.types.context import ProjectContext
from mtl.parser import ini
from mtl.utils.func import find, equals_insensitive, compiler_internal, search_file
from mtl.utils.constant import LEGAL_COMPILER_FLAGS

def loadDefinition(file: str) -> ProjectContext:
    ctx = ProjectContext(file)
    all_loaded: list[str] = []

    with open(file) as f:
        ctx.contents = ini.parse(f.read(), INIParserContext(file, Location(file, 0)))

    if (section := find(ctx.contents, lambda k: equals_insensitive(k.name, "Files"))) == None:
        raise TranslationError("Input definition file must contain a [Files] section.", compiler_internal())
    
    if (common := find(section.properties, lambda k: equals_insensitive(k.key, "stcommon"))) == None:
        raise TranslationError("Input definition file must specify common state file via `stcommon` key.", section.location)
    
    if (constants := find(section.properties, lambda k: equals_insensitive(k.key, "cns"))) == None:
        raise TranslationError("Input definition file must specify constants via `cns` key.", section.location)
    constants = search_file(constants.value, file)
    with open(constants) as f:
        ctx.constants = ini.parse(f.read(), INIParserContext(file, Location(file, 0)))

    if (commands := find(section.properties, lambda k: equals_insensitive(k.key, "cmd"))) == None:
        raise TranslationError("Input definition file must specify commands via `cmd` key.", section.location)
    commands = search_file(commands.value, file)
    with open(commands) as f:
        ctx.commands = ini.parse(f.read(), INIParserContext(file, Location(file, 0)))
    
    try:
        ctx.common_file = search_file(common.value, file, [f"stdlib/{common.value}"])
    except TranslationError:
        if common.value == "common1.cns":
            print(f"Attempting to load common states from built-in common1.mtl as {common.value} does not exist.")
            ctx.common_file = search_file("common1.mtl", file, [f"stdlib/common1.mtl"])
        else:
            raise
    all_loaded.append(ctx.common_file)

    if (st := find(section.properties, lambda k: equals_insensitive(k.key, "st"))) != None:
        target = search_file(st.value, file)
        if target not in all_loaded:
            all_loaded.append(target)
            ctx.source_files.append(target)

    if (cmd := find(section.properties, lambda k: equals_insensitive(k.key, "cmd"))) != None:
        target = search_file(cmd.value, file)
        if target not in all_loaded:
            all_loaded.append(target)
            ctx.source_files.append(target)

    ## support up to 1000 state files
    for i in range(1, 1000):
        if (st_next := find(section.properties, lambda k: equals_insensitive(k.key, f"st{i}"))) != None:
            target = search_file(st_next.value, file)
            if target not in all_loaded:
                all_loaded.append(target)
                ctx.source_files.append(target)
        else:
            break

    ## non-code files
    if (anim := find(section.properties, lambda k: equals_insensitive(k.key, "anim"))) != None:
        ctx.anim_file = search_file(anim.value, file)
    else:
        raise TranslationError("Input definition file must specify animation file via `anim` key.", section.location)
    if (sprite := find(section.properties, lambda k: equals_insensitive(k.key, "sprite"))) != None:
        ctx.spr_file = search_file(sprite.value, file)
    else:
        raise TranslationError("Input definition file must specify SFF file via `sprite` key.", section.location)
    if (sound := find(section.properties, lambda k: equals_insensitive(k.key, "sound"))) != None:
        ctx.snd_file = search_file(sound.value, file)
    else:
        raise TranslationError("Input definition file must specify SND file via `sound` key.", section.location)
    if (ai := find(section.properties, lambda k: equals_insensitive(k.key, "ai"))) != None:
        ctx.ai_file = search_file(ai.value, file)

    ## compiler flags
    if (section := find(ctx.contents, lambda k: equals_insensitive(k.name, "Compiler"))) != None:
        for property in section.properties:
            if property.key.lower() in LEGAL_COMPILER_FLAGS:
                ctx.compiler_flags.__dict__[property.key.lower()] = property.value.lower() == "true"

    return ctx