import time
import struct
import traceback

from mtl.debugging import process, database
from mtl.debugging.commands import DebuggerCommand, processDebugCommand

from mtl.types.translation import TypeCategory
from mtl.types.debugging import DebugParameterInfo, DebuggerTarget, DebuggingContext, DebugTypeInfo, DebuggerCommand, DebugProcessState

from mtl.utils.func import mask_variable, search_file, match_filenames
from mtl.utils.debug import get_state_by_id, get_state_by_name

def print_variable(base_addr: int, scope: str, var: DebugParameterInfo, debugger: DebuggerTarget, ctx: DebuggingContext):
    alloc = var.allocations[0]
    target_name = mask_variable(alloc[0], alloc[1], var.type.size, var.type.name == "float", var.system)
    target_value = process.getVariable(base_addr, alloc[0], alloc[1], var.type.size, var.type.name == "float", var.system, debugger, ctx)
    ## special handling for specific types:
    ### - `bool` should display as either `true` or `false`
    ### - `state` should display the state name, if available
    ### - `enum` and `flag` types should display the stored value
    if var.type.name == "bool": 
        target_value = "true" if target_value != 0 else "false"
    elif var.type.name == "state":
        if (state := next(filter(lambda k: str(k.id) == str(target_value), ctx.states), None)) != None:
            target_value = state.name
    elif var.type.category == TypeCategory.ENUM and isinstance(var.type, DebugTypeInfo):
        if int(target_value) < len(var.type.members):
            target_value = var.type.members[int(target_value)]
    elif var.type.category == TypeCategory.FLAG and isinstance(var.type, DebugTypeInfo):
        tv = int(target_value)
        target_value = ""
        flag = 0
        for member in var.type.members:
            if (tv & 2 ** flag) != 0: target_value += str(member)
            flag += 1

    print(f"{var.name:<32}\t{scope:<8}\t{var.type.name:<24}\t{target_name:<24}\t{target_value}")

def displayVariables(base_addr: int, p1_address: int, target: DebuggerTarget, ctx: DebuggingContext):
    state_id = process.getValue(base_addr + target.launch_info.database["stateno"], target, ctx)

    ## print all globals and all locals for the owner's statedef's scope.
    if (state := get_state_by_id(state_id, ctx)) == None: # type: ignore
        print(f"Couldn't determine the current state from state ID {state_id}.")
        return
    scope = state.scope
    ## display a header for the player
    player_id = process.getValue(base_addr + 0x04, target, ctx)
    helper_id = process.getValue(base_addr + target.launch_info.database["helperid"], target, ctx)
    player_scope = "Player" if base_addr == p1_address else f"Helper({helper_id})"
    player_name = process.getString(base_addr + 0x20, target, ctx)
    print(f"Player {player_id} - {player_scope} - {player_name}")
    print("========================================")
    ## display
    print(f"{'Name':<32}\t{'Scope':<8}\t{'Type':<24}\t{'Allocation':<24}\t{'Value':<16}")
    for var in ctx.globals:
        if var.scope == scope:
            print_variable(base_addr, "Global", var, target, ctx)
    for var in state.locals:
        print_variable(base_addr, "Local", var, target, ctx)

def displayMultipleVariables(scope: str, target: DebuggerTarget, ctx: DebuggingContext):
    ## fetch a list of all targets to display variables for.
    ## we have to suspend the process here otherwise the data will likely be junk!
    process.suspendExternal(target)

    ## iterate each player
    game_address = process.getValue(target.launch_info.database["game"], target, ctx)
    if game_address == 0:
        print("Can't fetch variables, game has not been initialized.")
        return
    p1_address = process.getValue(game_address + target.launch_info.database["player"], target, ctx)
    if p1_address == 0:
        print("Can't fetch variables, players have not been initialized.")
        return
    
    for idx in range(60):
        player_address = process.getValue(game_address + target.launch_info.database["player"] + idx * 4, target, ctx)
        if player_address == 0:
            continue
        root_address = process.getValue(player_address + target.launch_info.database["root_addr"], target, ctx)
        helper_id = process.getValue(player_address + target.launch_info.database["helperid"], target, ctx)
        if (player_address == p1_address and scope in ["all", "player"]) \
           or (root_address == p1_address and scope == "all") \
           or (root_address == p1_address and scope == f"helper({helper_id})"):
            ## display their variables
            displayVariables(player_address, p1_address, target, ctx)
            print("")

    process.resumeExternal(target)

def runDebugger(target: str, mugen: str, p2: str, ai: str):
    debugger = None

    ctx = database.load(target)

    ctx.p2_target = p2
    ctx.enable_ai = 1 if ai == "on" else 0

    print(f"Successfully loaded MTL debugging database from {target}.")

    print(f"mtldbg is ready, run `launch` to start debugging from MUGEN at {mugen}.")
    print(f"While MUGEN is running, press CTRL+C at any time to access the debug CLI.")
    command = DebuggerCommand.NONE
    while command != DebuggerCommand.EXIT:
        ## if the debugger state is EXIT, set debugger to None.
        if debugger != None and debugger.launch_info.state == DebugProcessState.EXIT:
            debugger = None
        ## if the process is not None, PAUSED, or SUSPENDED_WAIT, do not accept input.
        try:
            while debugger != None and debugger.launch_info.state not in [DebugProcessState.PAUSED, DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_DEBUG]:
                time.sleep(1/60)
                if debugger.launch_info.state == DebugProcessState.EXIT:
                    continue
        except KeyboardInterrupt:
            ## directly grants access to command prompt for one command
            pass

        request = processDebugCommand(input("> "))
        command = request.command_type

        if command == DebuggerCommand.EXIT and debugger != None and debugger.subprocess != None:
            print("Cannot exit debugger until the debug process is stopped (hint: run `stop` first).")
            command = DebuggerCommand.NONE
            continue

        try:
            if command == DebuggerCommand.LAUNCH:
                ## launch and attach MUGEN subprocess
                ## TODO: right now `breakpoints` is not cleared between launches.
                debugger = process.launch(mugen, target.replace(".mdbg.gen", ".def").replace(".mdbg", ".def"), ctx)
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
                process.removeStep(debugger, ctx)
                process.cont(debugger, ctx)
            elif command == DebuggerCommand.BREAK or command == DebuggerCommand.BREAKP:
                ## add a breakpoint; format of the breakpoint can be either <file>:<line> or <stateno> <ctrl index> or <state name> <ctrl index>
                if len(request.params) == 1:
                    # file:line
                    params = request.params[0].split(":")
                    filename = params[0]
                    line = int(params[1])
                    try:
                        filename = search_file(filename, target, [f"stdlib/{filename}"])
                    except:
                        print(f"Could not identify source file to use for {filename}.")
                        continue
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
                    elif debugger != None:
                        if command == DebuggerCommand.BREAK:
                            print(f"Created breakpoint {len(ctx.breakpoints) + 1} at: {match_location} (state {match[0]}, controller {match[1]})")
                            process.setBreakpoint(match[0], match[1], debugger, ctx)
                        elif command == DebuggerCommand.BREAKP:
                            ## TODO: convert to use new in-memory breakpoint function
                            print(f"Created passpoint {len(ctx.passpoints) + 1} at: {match_location} (state {match[0]}, controller {match[1]})")
                            process.setPasspoint(match[0], match[1], debugger, ctx)
                elif len(request.params) == 2:
                    # stateno index, just set it directly...
                    stateno = request.params[0]
                    try:
                        stateno = int(stateno)
                    except:
                        pass
                    state = None
                    if type(stateno) == int and (state := get_state_by_id(stateno, ctx)) == None:
                        print(f"Could not find any state with ID or name {stateno} for breakpoint.")
                        continue
                    elif type(stateno) == str and (state := get_state_by_name(stateno, ctx)) == None:
                        print(f"Could not find any state with ID or name {stateno} for breakpoint.")
                        continue

                    if state == None:
                        print(f"Could not find any state with ID or name {stateno} for breakpoint.")
                        continue
                    index = int(request.params[1])
                    if index >= len(state.states):
                        print(f"State with ID {stateno} only has {len(state.states)} controllers (controller indices are 0-indexed).")
                        continue
                    if command == DebuggerCommand.BREAK and debugger != None:
                        print(f"Created breakpoint {len(ctx.breakpoints) + 1} at: {state.states[index]} (state {stateno}, controller {index})")
                        process.setBreakpoint(state.id, index, debugger, ctx)
                    elif command == DebuggerCommand.BREAKP:
                        ## TODO: convert to use new in-memory breakpoint function
                        if debugger != None:
                            print(f"Created passpoint {len(ctx.passpoints) + 1} at: {state.states[index]} (state {stateno}, controller {index})")
                            process.setPasspoint(state.id, index, debugger, ctx)
                else:
                    print("Format of arguments to `break` command should either be <file>:<line> or <stateno> <ctrl index>.")
                    continue
            elif command == DebuggerCommand.STEP:
                ## step forward by 1 state controller.
                if debugger == None or debugger.subprocess == None:
                    print("Cannot continue when MUGEN has not been launched.")
                    continue
                process.cont(debugger, ctx)
            elif command == DebuggerCommand.DELETE:
                ## delete BP by ID.
                index = int(request.params[0])
                if index < 1 or index > len(ctx.breakpoints):
                    print(f"Could not find a breakpoint with ID {index}.")
                    continue
                ctx.breakpoints.remove(ctx.breakpoints[index - 1])
                ## update the table in-memory after removing.
                if debugger != None:
                    process.insertBreakpointTable(ctx.breakpoints, ctx.passpoints, debugger, ctx)
            elif command == DebuggerCommand.DELETEP:
                ## delete PP by ID.
                index = int(request.params[0])
                if index < 1 or index > len(ctx.passpoints):
                    print(f"Could not find a passpoint with ID {index}.")
                    continue
                ctx.passpoints.remove(ctx.passpoints[index - 1])
                ## update the table in-memory after removing.
                if debugger != None:
                    process.insertBreakpointTable(ctx.breakpoints, ctx.passpoints, debugger, ctx)
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
                elif request.params[0].lower() == "passpoints":
                    print(f"ID \t{'Location':<64}\tState")
                    for index in range(len(ctx.passpoints)):
                        bp = ctx.passpoints[index]
                        if (state := get_state_by_id(bp[0], ctx)) != None and bp[1] < len(state.states):
                            location = state.states[bp[1]]
                        else:
                            location = "<?>"
                        print(f"{index+1:<3}\t{str(location):<64}\t{bp[0]}, {bp[1]:<8}")
                elif request.params[0].lower() == "files":
                    print(f"Name")
                    all_files: list[str] = []
                    for state in ctx.states:
                        if state.location.filename not in all_files:
                            all_files.append(state.location.filename)
                        for controller in state.states:
                            if controller.filename not in all_files:
                                all_files.append(controller.filename)
                    for file in all_files:
                        print(file)
                elif request.params[0].lower() == "trigger":
                    if len(request.params) != 2:
                        print("Please provide a trigger name as argument to `info trigger` command.")
                        continue
                    if ctx.current_breakpoint == None or debugger == None:
                        print("Can't show trigger values unless a breakpoint has been reached.")
                        continue
                    if ctx.current_owner == 0:
                        print(f"Cannot get trigger values when the current owner is not known!")
                        continue
                    trigger = request.params[1].lower()
                    if trigger not in debugger.launch_info.database["triggers"]:
                        print(f"Offsets for trigger with name {request.params[1]} are not known; cannot display value.")
                        continue
                    offset = debugger.launch_info.database["triggers"][trigger]
                    raw_value = process.getValue(ctx.current_owner + offset[0], debugger, ctx)
                    if offset[1] == int:
                        value = raw_value
                    elif offset[1] == float:
                        value = struct.unpack('<f', raw_value.to_bytes(4, byteorder = 'little'))[0]
                    elif offset[1] == bool:
                        value = "true" if raw_value != 0 else "false"
                    else:
                        value = raw_value
                        print("Could not determine the value of trigger from its type; displaying integer value.")
                    print(f"{value}")
                elif request.params[0].lower() == "controller":
                    ## open the file specified by the breakpoint
                    if ctx.current_breakpoint == None or debugger == None:
                        print("Can't show controllers unless a breakpoint has been reached.")
                        continue
                    count = 1 if len(request.params) == 1 else int(request.params[1])
                    if (state := get_state_by_id(ctx.current_breakpoint[0], ctx)):
                        location = state.states[ctx.current_breakpoint[1]]
                        with open(location.filename) as f:
                            lines = f.readlines()
                        ## we know the exact line the controller starts at.
                        lines = lines[location.line-1:]
                        ## mtldbg needs to support both Python and CNS,
                        ## since mdk-python delegates its debugger to this.
                        ## so depending on file extension, we choose either Python or CNS controller identification.
                        if location.filename.endswith(".py"):
                            index = 0
                            bracket_open = False
                            bracket_count = 0
                            while index < len(lines):
                                for chara in lines[index]:
                                    if chara == "(": 
                                        bracket_open = True
                                        bracket_count += 1
                                    if chara == ")": bracket_count -= 1
                                    if bracket_open and bracket_count == 0: 
                                        count -= 1
                                        bracket_open = False
                                        break
                                if count == 0: break
                                index += 1
                            lines = lines[:index+1]
                            lines[-1] = lines[-1].rstrip()
                        else:
                            index = 1
                            while index < len(lines):
                                if lines[index].strip().startswith("["):
                                    count -= 1
                                if count == 0: break
                                index += 1
                            lines = lines[:index]
                        ## formatting
                        for index in range(len(lines)):
                            if lines[index].startswith("["): lines[index] = "\n" + lines[index]
                        print("".join([line for line in lines if len(line.strip()) != 0]))
                elif request.params[0].lower() == "variables":
                    ## if we are passed a scope, display variables for every character matching that scope.
                    if len(request.params) == 2:
                        if debugger == None:
                            print("Can't show variables unless the game has been launched.")
                            continue
                        if request.params[1].lower() in ["all", "player"] or request.params[1].lower().startswith("helper("):
                            displayMultipleVariables(request.params[1].lower(), debugger, ctx)
                            continue
                        else:
                            print(f"Can't show variables for unrecognized variable scope {request.params[1]} (should be one of all, player, or helper(xx))")
                            continue

                    ## otherwise display variables for the current player + statedef.
                    if ctx.current_breakpoint == None or debugger == None:
                        print("Can't show variables unless a breakpoint has been reached.")
                        continue
                    game_address = process.getValue(debugger.launch_info.database["game"], debugger, ctx)
                    if game_address == 0:
                        print("Can't fetch variables, game has not been initialized.")
                        return
                    p1_address = process.getValue(game_address + debugger.launch_info.database["player"], debugger, ctx)
                    if p1_address == 0:
                        print("Can't fetch variables, players have not been initialized.")
                        return
                    displayVariables(ctx.current_owner, p1_address, debugger, ctx)
            elif command == DebuggerCommand.STOP:
                if debugger == None or debugger.subprocess == None:
                    print("Cannot stop debugging when MUGEN has not been launched.")
                    continue
                ## continue the process.
                process.cont(debugger, ctx)
                ## set the process state so the other threads can exit
                if debugger != None: debugger.launch_info.state = DebugProcessState.EXIT
        except:
            traceback.print_exc()
            print("mtldbg encountered an error, please re-input a command.")
            continue