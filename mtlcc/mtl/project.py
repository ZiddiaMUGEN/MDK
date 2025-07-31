from mtl.types.shared import TranslationError, Location
from mtl.types.ini import INIParserContext
from mtl.types.context import ProjectContext
from mtl.parser import ini
from mtl.utils.func import find, equals_insensitive, compiler_internal, search_file


def loadDefinition(file: str) -> ProjectContext:
    ctx = ProjectContext(file)
    all_loaded: list[str] = []

    with open(file) as f:
        contents = ini.parse(f.read(), INIParserContext(file, Location(file, 0)))

    if (section := find(contents, lambda k: equals_insensitive(k.name, "Files"))) == None:
        raise TranslationError("Input definition file must contain a [Files] section.", compiler_internal())
    
    if (common := find(section.properties, lambda k: equals_insensitive(k.key, "stcommon"))) == None:
        raise TranslationError("Input definition file must specify common state file via `stcommon` key.", section.location)
    
    ctx.common_file = search_file(common.value, file, [f"stdlib/{common.value}"])
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

    for i in range(10):
        if (st_next := find(section.properties, lambda k: equals_insensitive(k.key, f"st{i}"))) != None:
            target = search_file(st_next.value, file)
            if target not in all_loaded:
                all_loaded.append(target)
                ctx.source_files.append(target)

    return ctx