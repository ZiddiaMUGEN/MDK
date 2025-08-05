## Debugging platform for MTL/CNS.
import argparse
import time
import readline

from mtl.types.debugging import DebugProcessState, DebugParameterInfo
from mtl.debugging import database, process
from mtl.debugging.commands import DebuggerCommand, processDebugCommand
from mtl.utils.func import match_filenames, find, mask_variable
from mtl.utils.debug import get_state_by_id

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
            ## TODO: right now `breakpoints` is not cleared between launches.
            debugger = process.launch(mugen, target.replace(".mdbg", ".def"), ctx)
        elif command == DebuggerCommand.LOAD:
            ## discard current mdbg and load a new one
            if debugger != None:
                print("Cannot change debugging database after MUGEN has been launched.")
                continue
            target = request.params[0]
            ctx = database.load(target)
            print(f"Successfully loaded MTL debugging database from {target}.")
        elif command == DebuggerCommand.CONTINUE:
            ## allow the process to continue running
            if debugger == None or debugger.subprocess == None:
                print("Cannot continue when MUGEN has not been launched.")
                continue
            process.cont(debugger)
        elif command == DebuggerCommand.BREAK:
            ## add a breakpoint; format of the breakpoint can be either <file>:<line> or <stateno> <ctrl index>
            if len(request.params) == 1:
                # file:line
                params = request.params[0].split(":")
                filename = params[0]
                line = int(params[1])
                # find the closest match to `filename:line` in the database,
                # which is either a statedef or a controller.
                # if it's a statedef set on controller 0.
                match = None
                match_location = None
                match_distance = 99999999
                for statedef in ctx.states:
                    if (fn := match_filenames(filename, statedef.location.filename)) != None:
                        if line >= statedef.location.line and (line - statedef.location.line) < match_distance:
                            match = (statedef.id, 0)
                            match_location = statedef.states[0]
                            match_location.filename = fn
                            match_distance = line - statedef.location.line
                        for cindex in range(len(statedef.states)):
                            controller = statedef.states[cindex]
                            if line >= controller.line and (line - controller.line) < match_distance:
                                match = (statedef.id, cindex)
                                match_location = controller
                                match_location.filename = fn
                                match_distance = line - controller.line
                if match == None:
                    print(f"Could not determine the state or controller to use for breakpoint {filename}:{line}")
                else:
                    print(f"Created breakpoint {len(ctx.breakpoints) + 1} at: {match_location} (state {match[0]}, controller {match[1]})")
                    ctx.breakpoints.append(match)
            elif len(request.params) == 2:
                # stateno index, just set it directly...
                stateno = int(request.params[0])
                index = int(request.params[1])
                if (state := get_state_by_id(stateno, ctx)) == None:
                    print(f"Could not find any state with ID {stateno} for breakpoint.")
                    continue
                if index >= len(state.states):
                    print(f"State with ID {stateno} only has {len(state.states)} controllers (controller indices are 0-indexed).")
                    continue
                print(f"Created breakpoint {len(ctx.breakpoints) + 1} at: {state.states[index]} (state {stateno}, controller {index})")
                ctx.breakpoints.append((stateno, index))
            else:
                print("Format of arguments to `break` command should either be <file>:<line> or <stateno> <ctrl index>.")
                continue
        elif command == DebuggerCommand.STEP:
            ## step forward by 1 state controller.
            if debugger == None or debugger.subprocess == None:
                print("Cannot continue when MUGEN has not been launched.")
                continue
            process.cont(debugger, step = True)
        elif command == DebuggerCommand.DELETE:
            ## delete BP by ID.
            index = int(request.params[0])
            if index < 1 or index > len(ctx.breakpoints):
                print(f"Could not find a breakpoint with ID {index}.")
                continue
            ctx.breakpoints.remove(ctx.breakpoints[index - 1])
        elif command == DebuggerCommand.EXIT:
            ## set the process state so the other threads can exit
            if debugger != None: debugger.launch_info.state = DebugProcessState.EXIT
        elif command == DebuggerCommand.INFO:
            ## display information.
            if request.params[0].lower() == "breakpoints":
                print(f"ID \t{'Location':<64}\tState")
                for index in range(len(ctx.breakpoints)):
                    bp = ctx.breakpoints[index]
                    if (state := get_state_by_id(bp[0], ctx)) != None and bp[1] < len(state.states):
                        location = state.states[bp[1]]
                    else:
                        location = "<?>"
                    print(f"{index+1:<3}\t{str(location):<64}\t{bp[0]}, {bp[1]:<8}")
            elif request.params[0].lower() == "variables":
                if ctx.current_breakpoint == None or debugger == None:
                    print("Can't show variables unless a breakpoint has been reached.")
                    continue
                ## print all globals and all locals for the current statedef's scope.
                if (state := get_state_by_id(ctx.current_breakpoint[0], ctx)) == None: # type: ignore
                    print(f"Couldn't determine the current state from breakpoint {ctx.current_breakpoint}.")
                    continue
                scope = state.scope
                ## collect all vars that apply to this state
                all_vars: list[DebugParameterInfo] = []
                for var in ctx.globals:
                    if var.scope == scope:
                        all_vars.append(var)
                for var in state.locals:
                    all_vars.append(var)
                ## display
                print(f"{'Name':<32}\t{'Type':<16}\t{'Allocation':<16}\t{'Value':<16}")
                for var in all_vars:
                    ## TODO: struct types, multiple allocations
                    alloc = var.allocations[0]
                    target_name = mask_variable(alloc[0], alloc[1], var.type.size, var.type.name == "float")
                    target_value = process.getVariable(alloc[0], alloc[1], var.type.size, var.type.name == "float", debugger)
                    if var.type.name == "bool": target_value = "true" if target_value != 0 else "false"
                    print(f"{var.name:<32}\t{var.type.name:<16}\t{target_name:<16}\t{target_value}")

        elif command == DebuggerCommand.STOP:
            if debugger == None or debugger.subprocess == None:
                print("Cannot stop debugging when MUGEN has not been launched.")
                continue
            ## continue the process.
            process.cont(debugger)
            ## set the process state so the other threads can exit
            if debugger != None: debugger.launch_info.state = DebugProcessState.EXIT
