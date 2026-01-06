import json
import traceback
import struct

from mtl.types.debugging import (
    DebugProcessState, DebuggerResponseIPC, DebuggerRequestIPC, DebuggerResponseType, 
    DebuggingContext, DebuggerTarget, DebugTypeInfo, TypeCategory
)
from mtl.debugging import database, process, common_function
from mtl.debugging.commands import DebuggerCommand, processDebugIPC, sendResponseIPC
from mtl.debugging.ipc_code import *

from mtl.utils.debug import get_state_by_id
from mtl.utils.func import search_file, match_filenames

def runDebuggerIPC(target: str, mugen: str, p2: str, ai: str):
    ## the early part of this function is identical to `runDebugger`.
    ## we just skip any `print` as we need to use stdio for IPC communication.
    debugger = None

    try:
        ctx = database.load(target)
    except:
        error_message = traceback.format_exc()
        error = {
            'message': error_message
        }
        sendResponseIPC(DebuggerResponseIPC(b'00000000-0000-0000-0000-000000000000', DebuggerCommand.IPC_EXIT, DebuggerResponseType.ERROR, DEBUGGER_INVALID_DEBUG_DATABASE))
        return

    ctx.p2_target = p2
    ctx.enable_ai = 1 if ai == "on" else 0
    ctx.quiet = True

    command = DebuggerCommand.NONE
    while command != DebuggerCommand.EXIT:
        ## if the debugger state is EXIT, set debugger to None.
        if debugger != None and debugger.launch_info.state == DebugProcessState.EXIT:
            while not debugger.subprocess.poll():
                ## re-continue the process in case it didn't continue earlier.
                process.cont(debugger, ctx, next_state = DebugProcessState.EXIT)
                process.resumeExternal(debugger)
                ## kill the process
                debugger.subprocess.terminate()
            debugger = None

        request = processDebugIPC()
        command = request.command_type

        if command == DebuggerCommand.EXIT and debugger != None and debugger.subprocess != None:
            sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_HELD_OPEN))
            command = DebuggerCommand.NONE
            continue

        try:
            if command == DebuggerCommand.LAUNCH:
                ## launch and attach MUGEN subprocess
                ## TODO: right now `breakpoints` is not cleared between launches.
                debugger = process.launch(mugen, target.replace(".mdbg.gen", ".def").replace(".mdbg", ".def"), ctx)
                debugger.launch_info.ipc = True
                sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.SUCCESS, json.dumps({ "pid": debugger.launch_info.process_id }).encode("utf-8")))
            elif command == DebuggerCommand.CONTINUE:
                ## allow the process to continue running
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue
                process.removeStep(debugger, ctx)
                process.cont(debugger, ctx)
                sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.SUCCESS, bytes()))
            elif command == DebuggerCommand.STEP:
                ## allow the process to continue running
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue
                process.cont(debugger, ctx)
                sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.SUCCESS, bytes()))
            elif command == DebuggerCommand.STOP:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue
                ## continue the process.
                process.cont(debugger, ctx, next_state = DebugProcessState.EXIT)
                process.resumeExternal(debugger)
                ## set the process state so the other threads can exit
                if debugger != None: debugger.launch_info.state = DebugProcessState.EXIT
                sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.SUCCESS, bytes()))
            elif command == DebuggerCommand.EXIT:
                ## set the process state so the other threads can exit
                if debugger != None:
                    debugger.launch_info.state = DebugProcessState.EXIT
                ## the exit thread can handle sending the quit request.
                #sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.SUCCESS, bytes()))
            elif command == DebuggerCommand.IPC_LIST_PLAYERS:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    return
                
                ipcListPlayers(request, debugger, ctx)
            elif command == DebuggerCommand.IPC_GET_PLAYER_INFO:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue

                ipcPlayerDetails(request, debugger, ctx)
            elif command == DebuggerCommand.IPC_GET_VARIABLES:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue

                ipcGetVariables(request, debugger, ctx)
            elif command == DebuggerCommand.IPC_GET_TRIGGER:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue

                ipcGetTrigger(request, debugger, ctx)
            elif command == DebuggerCommand.IPC_GET_TEAMSIDE:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue

                ipcGetTeamside(request, debugger, ctx)
            elif command == DebuggerCommand.IPC_CLEAR_BREAKPOINTS:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue

                ## get the path from the request
                params = json.loads(request.params.decode('utf-8'))
                if 'path' not in params:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_INVALID_INPUT))
                    continue

                ## check the path provided maps to a source file
                try:
                    path = search_file(params['path'], target)
                except:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_MISSING_SOURCE_FILE))
                    continue

                # clear all breakpoints which point to this path.
                ctx.breakpoints = list(filter(lambda k: not breakpointInFile(k, path, ctx), ctx.breakpoints))
                ctx.passpoints = list(filter(lambda k: not breakpointInFile(k, path, ctx), ctx.passpoints))
                ## update the table in-memory after removing.
                if debugger != None:
                    process.insertBreakpointTable(ctx.breakpoints, ctx.passpoints, debugger, ctx)
                
                sendResponseIPC(DebuggerResponseIPC(
                    request.message_id, command, DebuggerResponseType.SUCCESS, 
                    json.dumps(common_function.breakpointsToJson(ctx)).encode('utf-8')
                ))
            elif command == DebuggerCommand.IPC_SET_BREAKPOINT:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue

                ## get the path from the request
                params = json.loads(request.params.decode('utf-8'))
                if 'path' not in params or 'line' not in params or 'mode' not in params:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_INVALID_INPUT))
                    continue
                if params['mode'] not in ['bp', 'pp']:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_INVALID_INPUT))
                    continue

                ## check the path provided maps to a source file
                try:
                    path = search_file(params['path'], target)
                except:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_MISSING_SOURCE_FILE))
                    continue

                line = int(params['line'])
                mode = params['mode']

                created = common_function.insertBreakpoint(path, line, ctx, debugger, mode)

                sendResponseIPC(DebuggerResponseIPC(
                    request.message_id, command, DebuggerResponseType.SUCCESS, 
                    json.dumps(created).encode('utf-8')
                ))
            elif command == DebuggerCommand.IPC_PAUSE:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue

                if debugger.launch_info.state != DebugProcessState.RUNNING:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_ALREADY_PAUSED))
                    continue

                ## this is an immediate pause, does not involve the breakpoint system.
                ## i do not currently have a way to look up which character is executing code at this time,
                ## so we will just unset current_breakpoint and remove any step context.
                process.suspendExternal(debugger)
                debugger.launch_info.state = DebugProcessState.SUSPENDED_DEBUG

                ctx.current_breakpoint = None
                ctx.current_owner = 0
                process.removeStep(debugger, ctx)

                ## we send the first player ID through to the adapter to use as the 'thread ID' to pause on.
                game_address = process.getValue(debugger.launch_info.database["game"], debugger, ctx)
                if game_address == 0:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_GAME_NOT_INITIALIZED))
                    continue
                p1_address = process.getValue(game_address + debugger.launch_info.database["player"], debugger, ctx)
                if p1_address == 0:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYERS_NOT_INITIALIZED))
                    continue
                
                player_id = process.getValue(p1_address + 0x04, debugger, ctx)

                sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.SUCCESS, json.dumps({ "firstPlayerID": player_id }).encode('utf-8')))
            elif command == DebuggerCommand.IPC_SET_STEP_TARGET:
                if debugger == None or debugger.subprocess == None:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_NOT_RUNNING))
                    continue

                params = json.loads(request.params.decode('utf-8'))
                if 'player' not in params:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_INVALID_INPUT))
                    continue

                target_id = params['player']
                
                ## find the address of the provided player ID, then set it as the step owner
                game_address = process.getValue(debugger.launch_info.database["game"], debugger, ctx)
                if game_address == 0:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_GAME_NOT_INITIALIZED))
                    continue
                
                is_set = False
                for idx in range(60):
                    player_address = process.getValue(game_address + debugger.launch_info.database["player"] + idx * 4, debugger, ctx)
                    if player_address == 0:
                        continue
                    player_id = process.getValue(player_address + 0x04, debugger, ctx)
                    if player_id == target_id:
                        process.setStep(debugger, ctx, player_address)
                        is_set = True
                        break

                if is_set:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.SUCCESS, bytes()))
                else:
                    sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_PLAYER_NOT_EXIST))
            else:
                sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.ERROR, DEBUGGER_UNRECOGNIZED_COMMAND))
        except:
            error_message = traceback.format_exc()
            error = {
                'message': error_message,
                'send_params': request.params.decode('utf-8')
            }
            sendResponseIPC(DebuggerResponseIPC(request.message_id, command, DebuggerResponseType.EXCEPTION, json.dumps(error).encode('utf-8')))
            continue

def breakpointInFile(bp: tuple[int, int], path: str, ctx: DebuggingContext) -> bool:
    if (state := get_state_by_id(bp[0], ctx)) != None:
        if match_filenames(path, state.location.filename) != None:
            return True
    return False

def ipcListPlayers(request: DebuggerRequestIPC, debugger: DebuggerTarget, ctx: DebuggingContext):
    ## send a list of player IDs and names to the adapter.
    params = json.loads(request.params.decode('utf-8'))
    include_enemy = 'includeEnemy' in params and params['includeEnemy']

    ## we have to suspend the process here otherwise the data will likely be junk!
    if debugger.launch_info.state not in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT, DebugProcessState.PAUSED, DebugProcessState.SUSPENDED_DEBUG]:
        process.suspendExternal(debugger)

    ## iterate each player
    game_address = process.getValue(debugger.launch_info.database["game"], debugger, ctx)
    if game_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_GAME_NOT_INITIALIZED))
        return
    p1_address = process.getValue(game_address + debugger.launch_info.database["player"], debugger, ctx)
    if p1_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYERS_NOT_INITIALIZED))
        return

    results = common_function.listPlayers(game_address, p1_address, include_enemy, debugger, ctx)    
    
    if debugger.launch_info.state not in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT, DebugProcessState.PAUSED, DebugProcessState.SUSPENDED_DEBUG]:
        process.resumeExternal(debugger)

    sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.SUCCESS, json.dumps(results).encode('utf-8')))

def ipcPlayerDetails(request: DebuggerRequestIPC, debugger: DebuggerTarget, ctx: DebuggingContext):
    ## send the requested player's ID, name, and the current frame information
    params = json.loads(request.params.decode('utf-8'))
    if 'player' not in params:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_INVALID_INPUT))
        return
    
    target_id = params['player']

    ## we have to suspend the process here otherwise the data will likely be junk!
    if debugger.launch_info.state not in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT, DebugProcessState.PAUSED, DebugProcessState.SUSPENDED_DEBUG]:
        process.suspendExternal(debugger)

    ## iterate each player
    game_address = process.getValue(debugger.launch_info.database["game"], debugger, ctx)
    if game_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_GAME_NOT_INITIALIZED))
        return
    p1_address = process.getValue(game_address + debugger.launch_info.database["player"], debugger, ctx)
    if p1_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYERS_NOT_INITIALIZED))
        return

    target_address = 0
    for idx in range(60):
        player_address = process.getValue(game_address + debugger.launch_info.database["player"] + idx * 4, debugger, ctx)
        if player_address == 0:
            continue
            
        root_address = process.getValue(player_address + debugger.launch_info.database["root_addr"], debugger, ctx)
        player_id = process.getValue(player_address + 0x04, debugger, ctx)

        if target_id == player_id:
            if player_address != p1_address and root_address != p1_address:
                ## player with provided ID is owned by p2
                ## we can still provide SOME context for p2, we just can't provide a file name.
                player_name = process.getString(player_address + 0x20, debugger, ctx)
                player_state = process.getValue(player_address + debugger.launch_info.database["stateno"], debugger, ctx)

                ## if the player is custom-stated by a character owned by us, we can provide file info.
                fileName = "P2 data is not in debugging database and file cannot be retrieved."
                lineNumber = 1
                stateNameOrId = f"Unmanaged State {player_state}"

                if (owner := process.getValue(player_address + debugger.launch_info.database["state_owner"], debugger, ctx)) != 0xFFFFFFFF:
                    owner = owner - 1 ## for some ungodly reason this is 1-indexed, but flags -1 as invalid. wtf?
                    owner_addr = process.getValue(game_address + debugger.launch_info.database["player"] + owner * 4, debugger, ctx)
                    if owner_addr != 0 and process.getValue(owner_addr + debugger.launch_info.database["root_addr"], debugger, ctx) == p1_address:
                        if (state := get_state_by_id(player_state, ctx)) != None:
                            owner_name = process.getString(owner_addr + 0x20, debugger, ctx)
                            fileName = state.location.filename
                            lineNumber = state.location.line
                            stateNameOrId = f"{owner_name}'s Custom State {state.name}"

                            if player_address == ctx.current_owner and ctx.current_breakpoint != None:
                                ## player with provided ID is the current breakpoint holder, so we can display the exact controller
                                player_ctrl = ctx.current_breakpoint[1]
                                fileName = state.states[player_ctrl].filename
                                lineNumber = state.states[player_ctrl].line


                detailResult = {
                    "id": player_id,
                    "name": player_name,
                    "frame": {
                        "fileName": fileName,
                        "lineNumber": lineNumber,
                        "stateNameOrId": stateNameOrId
                    }
                }
                sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.SUCCESS, json.dumps(detailResult).encode('utf-8')))
                if debugger.launch_info.state not in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT, DebugProcessState.PAUSED, DebugProcessState.SUSPENDED_DEBUG]:
                    process.resumeExternal(debugger)
                return
            target_address = player_address
            break

    if target_address == 0:
        ## player with provided ID does not exist
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYER_NOT_EXIST))
        return
    
    if target_address == ctx.current_owner and ctx.current_breakpoint != None:
        ## player with provided ID is the current breakpoint holder, so we can display the exact controller
        player_name = process.getString(target_address + 0x20, debugger, ctx)
        player_state = ctx.current_breakpoint[0]
        player_ctrl = ctx.current_breakpoint[1]

        if (state := get_state_by_id(player_state, ctx)) == None:
            sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYER_INVALID_STATE))
            return

        detailResult = {
            "id": target_id,
            "name": player_name,
            "frame": {
                "fileName": state.states[player_ctrl].filename,
                "lineNumber": state.states[player_ctrl].line,
                "stateNameOrId": state.name
            }
        }
    else:
        ## player with provided ID is not the current breakpoint holder, so we can only display the state
        player_name = process.getString(target_address + 0x20, debugger, ctx)
        player_state = process.getValue(target_address + debugger.launch_info.database["stateno"], debugger, ctx)

        if (state := get_state_by_id(player_state, ctx)) == None:
            sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYER_INVALID_STATE))
            return

        detailResult = {
            "id": target_id,
            "name": player_name,
            "frame": {
                "fileName": state.location.filename,
                "lineNumber": state.location.line,
                "stateNameOrId": state.name
            }
        }

    sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.SUCCESS, json.dumps(detailResult).encode('utf-8')))

    if debugger.launch_info.state not in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT, DebugProcessState.PAUSED, DebugProcessState.SUSPENDED_DEBUG]:
        process.resumeExternal(debugger)

def ipcGetTeamside(request: DebuggerRequestIPC, debugger: DebuggerTarget, ctx: DebuggingContext):
    ## send a list of player IDs and names to the adapter.
    params = json.loads(request.params.decode('utf-8'))
    if 'player' not in params:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_INVALID_INPUT))
        return
    
    target_id = params['player']

    ## iterate each player
    game_address = process.getValue(debugger.launch_info.database["game"], debugger, ctx)
    if game_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_GAME_NOT_INITIALIZED))
        return
    p1_address = process.getValue(game_address + debugger.launch_info.database["player"], debugger, ctx)
    if p1_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYERS_NOT_INITIALIZED))
        return

    teamside = 0
    for idx in range(60):
        player_address = process.getValue(game_address + debugger.launch_info.database["player"] + idx * 4, debugger, ctx)
        if player_address == 0:
            continue

        root_address = process.getValue(player_address + debugger.launch_info.database["root_addr"], debugger, ctx)
        player_id = process.getValue(player_address + 0x04, debugger, ctx)
        if target_id == player_id:
            if player_address != p1_address and root_address != p1_address:
                teamside = 2
                ## in custom states we CAN treat as teamside=1 for variable display (it'll be sketchy though)
                if (owner := process.getValue(player_address + debugger.launch_info.database["state_owner"], debugger, ctx)) != 0xFFFFFFFF:
                    owner = owner - 1 ## for some ungodly reason this is 1-indexed, but flags -1 as invalid. wtf?
                    owner_addr = process.getValue(game_address + debugger.launch_info.database["player"] + owner * 4, debugger, ctx)
                    if owner_addr != 0 and process.getValue(owner_addr + debugger.launch_info.database["root_addr"], debugger, ctx) == p1_address:
                        teamside = 1
            else:
                teamside = 1
            break

    if teamside == 0:
        ## player with provided ID does not exist
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYER_NOT_EXIST))
        return
    
    sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.SUCCESS, json.dumps({ "teamside": teamside }).encode('utf-8')))

def ipcGetTrigger(request: DebuggerRequestIPC, debugger: DebuggerTarget, ctx: DebuggingContext):
    ## send a trigger value to the adapter.
    params = json.loads(request.params.decode('utf-8'))
    if 'player' not in params or 'trigger' not in params:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_INVALID_INPUT))
        return
    
    target_id = params['player']
    trigger_name: str = params['trigger']

    ## iterate each player
    game_address = process.getValue(debugger.launch_info.database["game"], debugger, ctx)
    if game_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_GAME_NOT_INITIALIZED))
        return
    p1_address = process.getValue(game_address + debugger.launch_info.database["player"], debugger, ctx)
    if p1_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYERS_NOT_INITIALIZED))
        return

    target_address = 0
    for idx in range(60):
        player_address = process.getValue(game_address + debugger.launch_info.database["player"] + idx * 4, debugger, ctx)
        if player_address == 0:
            continue

        player_id = process.getValue(player_address + 0x04, debugger, ctx)
        if target_id == player_id:
            target_address = player_address
            break

    if target_address == 0:
        ## player with provided ID does not exist
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYER_NOT_EXIST))
        return
    
    detailResult = common_function.getTriggerValue(trigger_name, target_address, game_address, debugger, ctx)
    if detailResult == None:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_VALUE_NOT_EXIST))
        return
    
    sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.SUCCESS, json.dumps(detailResult).encode('utf-8')))

def ipcGetVariables(request: DebuggerRequestIPC, debugger: DebuggerTarget, ctx: DebuggingContext):
    ## send a list of player IDs and names to the adapter.
    params = json.loads(request.params.decode('utf-8'))
    if 'player' not in params or 'type' not in params:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_INVALID_INPUT))
        return
    
    target_id = params['player']
    variable_type = params['type']

    ## iterate each player
    game_address = process.getValue(debugger.launch_info.database["game"], debugger, ctx)
    if game_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_GAME_NOT_INITIALIZED))
        return
    p1_address = process.getValue(game_address + debugger.launch_info.database["player"], debugger, ctx)
    if p1_address == 0:
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYERS_NOT_INITIALIZED))
        return

    target_address = 0
    for idx in range(60):
        player_address = process.getValue(game_address + debugger.launch_info.database["player"] + idx * 4, debugger, ctx)
        if player_address == 0:
            continue

        player_id = process.getValue(player_address + 0x04, debugger, ctx)
        if target_id == player_id:
            target_address = player_address
            break

    if target_address == 0:
        ## player with provided ID does not exist
        sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.ERROR, DEBUGGER_PLAYER_NOT_EXIST))
        return
    
    player_state = process.getValue(target_address + debugger.launch_info.database["stateno"], debugger, ctx)
    state = get_state_by_id(player_state, ctx)
    
    ## handle the specific type of variable request
    detailResult = []
    if (variable_type == "GLOBAL" or variable_type == "ALL") and state != None:
        for var in ctx.globals:
            if var.scope == state.scope and isinstance(var.type, DebugTypeInfo):
                detailResult.append({
                    "name": var.name,
                    "value": common_function.get_typed_value(
                        var.type,
                        process.getVariable(target_address, var.allocations[0][0], var.allocations[0][1], var.type.size, var.type.name == "float", var.system, debugger, ctx),
                        ctx
                    )
                })
    if (variable_type == "LOCAL" or variable_type == "ALL") and state != None:
        for var in state.locals:
            if isinstance(var.type, DebugTypeInfo):
                detailResult.append({
                    "name": var.name,
                    "value": common_function.get_typed_value(
                        var.type,
                        process.getVariable(target_address, var.allocations[0][0], var.allocations[0][1], var.type.size, var.type.name == "float", var.system, debugger, ctx),
                        ctx
                    )
                })
    if (variable_type == "AUTO" or variable_type == "ALL") and state != None:
        triggers: list[str] = []
        for ctrl in state.state_data:
            for trigger in ctrl.triggers:
                if trigger not in triggers:
                    triggers.append(trigger)
        for trigger in triggers:
            nextResult = common_function.getTriggerValue(trigger, target_address, game_address, debugger, ctx)
            if nextResult != None:
                detailResult.append(nextResult)
            else:
                detailResult.append({
                    "name": trigger,
                    "value": "No offset for trigger"
                })
    if variable_type == "INDEXED_INT" or variable_type == "ALL":
        for idx in range(60):
            detailResult.append({
                "name": f"var({idx})",
                "value": process.getVariable(target_address, idx, 0, 32, False, False, debugger, ctx)
            })
    if variable_type == "INDEXED_FLOAT" or variable_type == "ALL":
        for idx in range(40):
            detailResult.append({
                "name": f"fvar({idx})",
                "value": process.getVariable(target_address, idx, 0, 32, True, False, debugger, ctx)
            })
    if variable_type == "INDEXED_SYSINT" or variable_type == "ALL":
        for idx in range(5):
            detailResult.append({
                "name": f"sysvar({idx})",
                "value": process.getVariable(target_address, idx, 0, 32, False, True, debugger, ctx)
            })
    if variable_type == "INDEXED_SYSFLOAT" or variable_type == "ALL":
        for idx in range(5):
            detailResult.append({
                "name": f"sysfvar({idx})",
                "value": process.getVariable(target_address, idx, 0, 32, True, True, debugger, ctx)
            })

    ## we have to suspend the process here otherwise the data will likely be junk!
    if debugger.launch_info.state not in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT, DebugProcessState.PAUSED, DebugProcessState.SUSPENDED_DEBUG]:
        process.suspendExternal(debugger)

    sendResponseIPC(DebuggerResponseIPC(request.message_id, request.command_type, DebuggerResponseType.SUCCESS, json.dumps(detailResult).encode('utf-8')))

    if debugger.launch_info.state not in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT, DebugProcessState.PAUSED, DebugProcessState.SUSPENDED_DEBUG]:
        process.resumeExternal(debugger)