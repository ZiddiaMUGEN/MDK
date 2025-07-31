import argparse
import traceback
import os

from mtl import loader, translator, project
from mtl.utils.compiler import TranslationError
from mtl.utils.func import find, equals_insensitive

from mtl.types.context import *

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='mtlcc', description='Translation tool from MTL templates into CNS character code')
    parser.add_argument('input', help='Path to the DEF file containing the character to translate')

    args = parser.parse_args()
    ## note: the spec states that translation of included files should stop at step 3.
    ## this is guaranteed by having steps up to 3 in `loadFile`, and remaining steps handled in `translateContext`.
    try:
        projectContext = project.loadDefinition(args.input)
        ## we perform a load of each file sequentially and combine the loadContext,
        ## then pass it all to translation at once.
        ## this means imports should be done ONCE ONLY,
        ## and global variables will be SHARED.
        loadContext = loader.loadFile(projectContext.common_file, [])
        # mark all common states as such
        for defn in loadContext.state_definitions:
            defn.is_common = True

        for source_file in projectContext.source_files:
            nextLoadContext = loader.loadFile(source_file, [])
            # only overwrite common state definitions. otherwise emit an error
            for defn in nextLoadContext.state_definitions:
                if (existing := find(loadContext.state_definitions, lambda k: equals_insensitive(k.name, defn.name))) == None:
                    loadContext.state_definitions.append(defn)
                elif existing.is_common:
                    loadContext.state_definitions.remove(existing)
                    loadContext.state_definitions.append(defn)
                else:
                    raise TranslationError(f"Attempted to redefine a non-common state {defn.name} (previously defined at {os.path.realpath(existing.location.filename)}:{existing.location.line})", defn.location)
            # for triggers, apply them if they are not matched. if they are matched, skip if it's the same source; otherwise emit an error.
            for trig in nextLoadContext.triggers:
                trig_name = trig.name
                if trig.namespace != None: trig_name = f"{trig.namespace}.{trig_name}"
                if (existing := find(loadContext.triggers, lambda k: equals_insensitive(k.name, trig_name))) == None:
                    loadContext.triggers.append(trig)
                elif existing.location != trig.location:
                    raise TranslationError(f"Attempted to redefine a trigger {trig.name} (previously defined at {os.path.realpath(existing.location.filename)}:{existing.location.line})", trig.location)
            # for templates, apply them if they are not matched. if they are matched, skip if it's the same source; otherwise emit an error.
            for templ in nextLoadContext.templates:
                templ_name = templ.name
                if templ.namespace != None: templ_name = f"{templ.namespace}.{templ_name}"
                if (existing := find(loadContext.templates, lambda k: equals_insensitive(k.name, templ_name))) == None:
                    loadContext.templates.append(templ)
                elif existing.location != templ.location:
                    raise TranslationError(f"Attempted to redefine a template {templ.name} (previously defined at {os.path.realpath(existing.location.filename)}:{existing.location.line})", templ.location)
            # for types, apply them if they are not matched. if they are matched, skip if it's the same source; otherwise emit an error.
            for typedef in nextLoadContext.type_definitions:
                type_name = typedef.name
                if typedef.namespace != None: type_name = f"{typedef.namespace}.{type_name}"
                if (existing := find(loadContext.type_definitions, lambda k: equals_insensitive(k.name, type_name))) == None:
                    loadContext.type_definitions.append(typedef)
                elif existing.location != typedef.location:
                    raise TranslationError(f"Attempted to redefine a type {typedef.name} (previously defined at {os.path.realpath(existing.location.filename)}:{existing.location.line})", typedef.location)
            for struct in nextLoadContext.struct_definitions:
                struct_name = struct.name
                if struct.namespace != None: struct_name = f"{struct.namespace}.{struct_name}"
                if (existing := find(loadContext.struct_definitions, lambda k: equals_insensitive(k.name, struct_name))) == None:
                    loadContext.struct_definitions.append(struct)
                elif existing.location != struct.location:
                    raise TranslationError(f"Attempted to redefine a type {struct.name} (previously defined at {os.path.realpath(existing.location.filename)}:{existing.location.line})", struct.location)
            # for includes, apply them if they are not matched. if they are matched, skip if it's the same source; otherwise emit an error.
            for incl in nextLoadContext.includes:
                if (existing := find(loadContext.includes, lambda k: equals_insensitive(k.name, incl.name))) == None:
                    loadContext.includes.append(incl)
                elif existing.location != incl.location:
                    raise TranslationError(f"Attempted to redefine an include {incl.name} (previously defined at {os.path.realpath(existing.location.filename)}:{existing.location.line})", incl.location)

        ## includes must be processed against the COMBINED context,
        ## so the processIncludes call has to be moved out to here.
        # create a virtual include for libmtl.inc.
        # libmtl.inc has several required types for the builtins to function.
        loadContext.includes.insert(0, loader.get_libmtl())
        loader.processIncludes([], loadContext)

        translated = translator.translateContext(loadContext)

        with open(os.path.splitext(args.input)[0] + ".generated.cns", mode="w") as f:
            f.writelines(s + "\n" for s in translator.createOutput(translated))
    except TranslationError as exc:
        py_exc = traceback.format_exc().split("\n")[-4].strip()
        print("Translation terminated with an error.")
        print(f"\t{exc.message}")
        print(f"mtlcc exception source: {py_exc}")