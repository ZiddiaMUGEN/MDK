## Debugging platform for MTL/CNS.
import argparse
# readline is required for command history. but it's not available on Windows.
# the pyreadline3 library works as a replacement?
import readline

from mtl.debugging.cli_function import runDebugger
from mtl.debugging.ipc_function import runDebuggerIPC
from mtl.debugging.common_function import generate
from mtl.debugging.commands import DebuggerCommand, sendResponseIPC
from mtl.types.debugging import DebuggerResponseIPC, DebuggerResponseType

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
        if args.ipc:
            sendResponseIPC(DebuggerResponseIPC(b'00000000-0000-0000-0000-000000000000', DebuggerCommand.IPC_GENERATE, DebuggerResponseType.SUCCESS, bytes()))
        else:
            print("Waiting for debugging database to generate.")
        target = generate(target, args.generate, mugen)

    if args.ipc:
        runDebuggerIPC(target, mugen, p2, ai)
    else:
        runDebugger(target, mugen, p2, ai)

if __name__ == "__main__":
    debug()
