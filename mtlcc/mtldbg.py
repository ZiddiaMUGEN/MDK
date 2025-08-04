## Debugging platform for MTL/CNS.
import argparse
import readline

from mtl.debugging import database, process
from mtl.debugging.commands import DebuggerCommand, processDebugCommand

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='mtldbg', description='Debugger for MTL and CNS characters compiled by MTL')
    parser.add_argument('-d', '--database', help='Path to the mdbg file containing debugger definitions', required=True)
    parser.add_argument('-m', '--executable', help='Path to the mugen.exe executable for the MUGEN installation to use', required=True)

    args = parser.parse_args()

    target = args.database
    mugen = args.executable
    subprocess = None

    ctx = database.load(target)
    print(f"Successfully loaded MTL debugging database from {target}.")

    print(f"mtldbg is ready, run `launch` to start debugging from MUGEN at {mugen}.")
    command = DebuggerCommand.NONE
    while command != DebuggerCommand.EXIT:
        request = processDebugCommand(input("> "))
        command = request.command_type

        if command == DebuggerCommand.LAUNCH:
            ## launch and attach MUGEN subprocess
            subprocess = process.launch(mugen, target.replace(".mdbg", ".def"))
        elif command == DebuggerCommand.LOAD:
            ## discard current mdbg and load a new one
            target = request.params[0]
            ctx = database.load(target)
            print(f"Successfully loaded MTL debugging database from {target}.")
