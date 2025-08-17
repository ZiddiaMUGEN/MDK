import argparse
import traceback
import os
import shutil

from mtl import loader, translator, project
from mtl.utils.compiler import TranslationError
from mtl.utils.func import find, equals_insensitive, includes_insensitive
from mtl.debugging import database

from mtl.types.context import *

## this is exported to a separate file so the mdk-python compiler can launch with
## an explicitly-passed and modified ProjectContext.
def runCompilerFromDef(input: str, output: str, projectContext: ProjectContext):
    ## note: the spec states that translation of included files should stop at step 3.
    ## this is guaranteed by having steps up to 3 in `loadFile`, and remaining steps handled in `translateContext`.
    try:
        ## we perform a load of each file sequentially and combine the loadContext,
        ## then pass it all to translation at once.
        ## this means imports should be done ONCE ONLY,
        ## and global variables will be SHARED.
        loadContext = loader.loadFile(projectContext.common_file, projectContext.compiler_flags, [])
        # mark all common states as such
        for defn in loadContext.state_definitions:
            defn.is_common = True

        for source_file in projectContext.source_files:
            nextLoadContext = loader.loadFile(source_file, projectContext.compiler_flags, [])
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
                source = find(incl.properties, lambda k: k.key.lower() == "source")
                if source == None: raise TranslationError("The 'source' property is required on Include blocks.", incl.location)
                for existing in loadContext.includes:
                    existing_source = find(existing.properties, lambda k: k.key.lower() == "source")
                    if existing_source == None: raise TranslationError("The 'source' property is required on Include blocks.", existing.location)
                    if source.value == existing_source.value:
                        raise TranslationError(f"Attempted to redefine an include {incl.name} (previously defined at {os.path.realpath(existing.location.filename)}:{existing.location.line})", incl.location)
                loadContext.includes.append(incl)

        ## includes must be processed against the COMBINED context,
        ## so the processIncludes call has to be moved out to here.
        # create a virtual include for libmtl.inc.
        # libmtl.inc has several required types for the builtins to function.
        loadContext.includes.insert(0, loader.get_libmtl(loadContext.compiler_flags))
        loader.processIncludes([], loadContext)

        loadContext.global_forwards = projectContext.global_forwards

        loadContext.filename = os.path.abspath(input)
        translated = translator.translateContext(loadContext)
        translated.filename = os.path.abspath(input)

        ## create output directory
        if not os.path.exists(output):
            os.makedirs(output)
        ## identify target file
        target_file = os.path.realpath(output) + "/" + os.path.basename(os.path.splitext(input)[0] + ".st")

        print(f"Start writing output states to state file {target_file}.")
        with open(target_file, mode="w") as f:
            f.writelines(s + "\n" for s in translator.createOutput(translated))
        print("Done writing state data.")

        ## generate debugging info
        debug_file = os.path.realpath(output) + "/" + os.path.basename(os.path.splitext(input)[0] + ".mdbg")
        translated.debugging.filename = os.path.abspath(input)
        print(f"Start writing debugging database to file {debug_file}.")
        database.writeDatabase(debug_file, translated.debugging)
        print("Done writing debugging data.")

        ## emit CNS constants file
        target_cns = os.path.realpath(output) + "/" + os.path.basename(os.path.splitext(input)[0] + ".constants")
        with open(target_cns, mode="w") as f:
            for section in projectContext.constants:
                if includes_insensitive(section.name, ["Data", "Size", "Velocity", "Movement", "Quotes"]):
                    f.write(f"[{section.name}]\n")

                    for property in section.properties:
                        f.write(f"{property.key} = {property.value}\n")
                    
                    f.write("\n")

        ## emit CMD file
        target_cns = os.path.realpath(output) + "/" + os.path.basename(os.path.splitext(input)[0] + ".commands")
        with open(target_cns, mode="w") as f:
            for section in projectContext.commands:
                if includes_insensitive(section.name, ["Command", "Remap", "Defaults"]):
                    f.write(f"[{section.name}]\n")

                    for property in section.properties:
                        f.write(f"{property.key} = {property.value}\n")
                    
                    f.write("\n")
            ## the CMD file needs a statedef to load.
            ## attach a super-invalid one just to get it to load.
            ## (if anyone is exploiting to use -111 they should also know enough to fix this).
            f.write("[Statedef -111]\n[State -111]\ntype = Null\ntrigger1 = 1")

        ## emit DEF file
        target_def = os.path.realpath(output) + "/" + os.path.basename(os.path.splitext(input)[0] + ".def")
        with open(target_def, mode="w") as f:
            f.write("[Files]\n")
            ## since we always import a MTL-ready common1, we can use builtin here
            f.write("stcommon = common1.cns\n")
            f.write(f"st = {os.path.basename(os.path.splitext(input)[0] + '.st')}\n")
            f.write(f"cmd = {os.path.basename(os.path.splitext(input)[0] + '.commands')}\n")
            f.write(f"cns = {os.path.basename(os.path.splitext(input)[0] + '.constants')}\n")

            target_spr =  os.path.realpath(output) + "/" + os.path.basename(projectContext.spr_file)
            shutil.copy(projectContext.spr_file, target_spr)
            f.write(f"sprite = {os.path.basename(projectContext.spr_file)}\n")

            target_snd =  os.path.realpath(output) + "/" + os.path.basename(projectContext.snd_file)
            shutil.copy(projectContext.snd_file, target_snd)
            f.write(f"sound = {os.path.basename(projectContext.snd_file)}\n")

            target_air =  os.path.realpath(output) + "/" + os.path.basename(projectContext.anim_file)
            shutil.copy(projectContext.anim_file, target_air)
            f.write(f"anim = {os.path.basename(projectContext.anim_file)}\n")

            if projectContext.ai_file != None:
                target_ai =  os.path.realpath(output) + "/" + os.path.basename(projectContext.ai_file)
                shutil.copy(projectContext.ai_file, target_ai)
                f.write(f"ai = {os.path.basename(projectContext.ai_file)}\n")
            
            f.write("\n")

            for section in projectContext.contents:
                if equals_insensitive(section.name, "Files"):
                    continue
                    
                f.write(f"[{section.name}]\n")

                for property in section.properties:
                    f.write(f"{property.key} = {property.value}\n")
                
                f.write("\n")

    except TranslationError as exc:
        py_exc = traceback.format_exc().split("\n")[-4].strip()
        print("Translation terminated with an error.")
        print(f"\t{exc.message}")
        print(f"mtlcc exception source: {py_exc}")

def runCompiler(input: str, output: str):
    projectContext = project.loadDefinition(input)
    runCompilerFromDef(input, output, projectContext)

def compile():
    parser = argparse.ArgumentParser(prog='mtlcc', description='Translation tool from MTL templates into CNS character code')
    parser.add_argument('input', help='Path to the DEF file containing the character to translate')
    parser.add_argument('output', help='Path to the folder to write the resulting character to')

    args = parser.parse_args()

    runCompiler(args.input, args.output)

if __name__ == "__main__":
    compile()

__all__ = ["runCompiler", "runCompilerFromDef"]