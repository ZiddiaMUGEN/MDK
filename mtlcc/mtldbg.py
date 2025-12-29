## Debugging platform for MTL/CNS.
import argparse
# readline is required for command history. but it's not available on Windows.
# the pyreadline3 library works as a replacement?
import readline
import sys

from mtl.debugging.cli_function import runDebugger
from mtl.debugging.ipc_function import runDebuggerIPC

from mtl.project import loadDefinition
from mtl.types.translation import StateDefinition, StateDefinitionParameters, StateDefinitionScope, StateScopeType, StateController
from mtl.types.context import LoadContext, CompilerConfiguration, TranslationMode
from mtl.parser import ini
from mtl.loader import parseTarget
from mtl.debugging.database import loadStates, writeDatabase

def debug():
    parser = argparse.ArgumentParser(prog='mtldbg', description='Debugger for MTL and CNS characters compiled by MTL')
    parser.add_argument('-d', '--database', help='Path to the mdbg file containing debugger definitions', required=True)
    parser.add_argument('-m', '--executable', help='Path to the mugen.exe executable for the MUGEN installation to use', required=True)
    parser.add_argument('-p', '--p2name', help='Name of the character to use as P2', required=False)
    parser.add_argument('-a', '--enableai', help='Set to `on` to enable AI in the fight', required=False)
    parser.add_argument('-i', '--ipc', help='Enable IPC for the debugger instead of an interactive CLI', required=False, action='store_true')
    parser.add_argument('-g', '--generate', help='Path to a DEF file to use for generating a new debugging database (for CNS characters)', required=False)

    args = parser.parse_args()

    target = args.database
    mugen = args.executable

    p2 = args.p2name if args.p2name else "kfm"
    ai = args.enableai if args.enableai else "off"

    if args.generate:
        target = generate(target, args.generate)

    if args.ipc:
        runDebuggerIPC(target, mugen, p2, ai)
    else:
        runDebugger(target, mugen, p2, ai)

def generate(database: str, character: str):
    result = f"{database}.gen"
    ## read the DEF file as provided
    definition = loadDefinition(character)
    ## read each state file from the DEF file into a list of StateDefinition
    states: list[StateDefinition] = []
    ### each StateDefinition here only needs to define `name`, `states`, and `location`.
    ### both `locals` and `parameters` are not valid in CNS, and `scope` should always be global.
    for source in definition.source_files:
        loadContext = LoadContext(source, CompilerConfiguration())

        with open(source, errors='ignore') as f:
            contents = ini.parse(f.read(), loadContext.ini_context)
            parseTarget(contents, TranslationMode.CNS_MODE, loadContext, True)
            for state in loadContext.state_definitions:
                new_definition = StateDefinition(state.name, StateDefinitionParameters(), [], [], StateDefinitionScope(StateScopeType.SHARED, None), state.location)
                for controller in state.states:
                    ## the contents of the controller do not matter. we just need the locations.
                    new_definition.states.append(StateController("", {}, [], controller.location))
                states.append(new_definition)
    ## process the StateDefinitions into a minimal debugging context
    context = loadStates(states, character)
    ## write the states into the `.gen` database file
    writeDatabase(result, context)
    return result

if __name__ == "__main__":
    debug()
