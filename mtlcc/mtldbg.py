## Debugging platform for MTL/CNS.
import argparse
import time
import readline

from mtl.types.debugging import DebugProcessState
from mtl.debugging import database, process
from mtl.debugging.commands import DebuggerCommand, processDebugCommand

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='mtldbg', description='Debugger for MTL and CNS characters compiled by MTL')
    parser.add_argument('-d', '--database', help='Path to the mdbg file containing debugger definitions', required=True)
    parser.add_argument('-m', '--executable', help='Path to the mugen.exe executable for the MUGEN installation to use', required=True)

    args = parser.parse_args()

    target = args.database
    mugen = args.executable
    debugger = None

    ctx = database.load(target)
    print(f"Successfully loaded MTL debugging database from {target}.")

    print(f"mtldbg is ready, run `launch` to start debugging from MUGEN at {mugen}.")
    command = DebuggerCommand.NONE
    while command != DebuggerCommand.EXIT:
        ## if the debugger state is EXIT, set debugger to None.
        if debugger != None and debugger.launch_info.state == DebugProcessState.EXIT:
            debugger = None
        ## if the process is not None, PAUSED, or SUSPENDED_WAIT, do not accept input.
        if debugger != None and debugger.launch_info.state not in [DebugProcessState.PAUSED, DebugProcessState.SUSPENDED_PROCEED]:
            time.sleep(1/60)
            continue

        request = processDebugCommand(input("> "))
        command = request.command_type

        if command == DebuggerCommand.LAUNCH:
            ## launch and attach MUGEN subprocess
            debugger = process.launch(mugen, target.replace(".mdbg", ".def"))
        elif command == DebuggerCommand.LOAD:
            ## discard current mdbg and load a new one
            target = request.params[0]
            ctx = database.load(target)
            print(f"Successfully loaded MTL debugging database from {target}.")
        elif command == DebuggerCommand.CONTINUE:
            ## allow the process to continue running
            if debugger == None or debugger.subprocess == None:
                print("Cannot continue when MUGEN has not been launched.")
                continue
            process.cont(debugger)
        elif command == DebuggerCommand.EXIT:
            ## set the process state so the other threads can exit
            if debugger != None: debugger.launch_info.state = DebugProcessState.EXIT
