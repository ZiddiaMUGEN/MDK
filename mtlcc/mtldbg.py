## Debugging platform for MTL/CNS.
import argparse
# readline is required for command history. but it's not available on Windows.
# the pyreadline3 library works as a replacement?
import readline

from mtl.debugging.cli_function import runDebugger
from mtl.debugging.ipc_function import runDebuggerIPC

def debug():
    parser = argparse.ArgumentParser(prog='mtldbg', description='Debugger for MTL and CNS characters compiled by MTL')
    parser.add_argument('-d', '--database', help='Path to the mdbg file containing debugger definitions', required=True)
    parser.add_argument('-m', '--executable', help='Path to the mugen.exe executable for the MUGEN installation to use', required=True)
    parser.add_argument('-p', '--p2name', help='Name of the character to use as P2', required=False)
    parser.add_argument('-a', '--enableai', help='Set to `on` to enable AI in the fight', required=False)
    parser.add_argument('-i', '--ipc', help='Pass `-i` to enable IPC with the debugger instead of an interactive CLI', required=False, action='store_true')

    args = parser.parse_args()

    target = args.database
    mugen = args.executable

    p2 = args.p2name if args.p2name else "kfm"
    ai = args.enableai if args.enableai else "off"

    if args.ipc:
        runDebuggerIPC(target, mugen, p2, ai)
    else:
        runDebugger(target, mugen, p2, ai)

if __name__ == "__main__":
    debug()
