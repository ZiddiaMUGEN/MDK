## shared functions between IPC and CLI modes
## these are higher-level functions than those in process.py, which don't interact with the subprocess directly.

import os
import struct

from mtl.types.translation import StateDefinition, StateDefinitionParameters, StateDefinitionScope, StateScopeType, StateController, TypeCategory
from mtl.types.context import LoadContext, CompilerConfiguration, TranslationMode
from mtl.types.debugging import DebuggingContext, DebuggerTarget, DebugTypeInfo

from mtl.utils.func import match_filenames
from mtl.utils.debug import get_state_by_id

from mtl.project import loadDefinition
from mtl.parser import ini
from mtl.loader import parseTarget
from mtl.debugging.database import loadStates, writeDatabase

from mtl.debugging import process

def generate(database: str, character: str, mugen: str):
    result = f"{database}.gen"
    ## read the DEF file as provided
    definition = loadDefinition(character, True)
    if definition.common_file.endswith("common1.mtl"):
        ## this indicates the character uses builtin common1.cns.
        definition.common_file = os.path.dirname(os.path.abspath(mugen)) + "/data/common1.cns"
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
                new_definition.parameters.id = int(state.name)
                for controller in state.states:
                    ## the contents of the controller do not matter. we just need the locations.
                    new_definition.states.append(StateController("", {}, [], controller.location))
                states.append(new_definition)
    loadContext = LoadContext(definition.common_file, CompilerConfiguration())
    with open(definition.common_file, errors='ignore') as f:
        contents = ini.parse(f.read(), loadContext.ini_context)
        parseTarget(contents, TranslationMode.CNS_MODE, loadContext, True)
        for state in loadContext.state_definitions:
            new_definition = StateDefinition(state.name, StateDefinitionParameters(), [], [], StateDefinitionScope(StateScopeType.SHARED, None), state.location)
            new_definition.parameters.id = int(state.name)
            new_definition.parameters.is_common = True
            for controller in state.states:
                ## the contents of the controller do not matter. we just need the locations.
                new_definition.states.append(StateController("", {}, [], controller.location))
            states.append(new_definition)
    ## process the StateDefinitions into a minimal debugging context
    context = loadStates(states, character)
    ## write the states into the `.gen` database file
    writeDatabase(result, context)
    return result

def insertBreakpoint(filename: str, line: int, ctx: DebuggingContext, debugger: DebuggerTarget, mode: str) -> dict | None:
    if mode not in ["bp", "pp"]:
        raise Exception(f"Invalid breakpoint mode {mode}")
    # find the closest match to `filename:line` in the database,
    # which is either a statedef or a controller.
    # if it's a statedef set on controller 0.
    match = None
    match_location = None
    match_distance = 99999999
    for statedef in ctx.states:
        if match_filenames(filename, statedef.location.filename) != None:
            if line >= statedef.location.line and (line - statedef.location.line) < match_distance:
                match = (statedef.id, 0)
                match_location = statedef.states[0]
                match_distance = line - statedef.location.line
            for cindex in range(len(statedef.states)):
                controller = statedef.states[cindex]
                if line >= controller.line and (line - controller.line) < match_distance and match_filenames(filename, controller.filename) != None:
                    match = (statedef.id, cindex)
                    match_location = controller
                    match_distance = line - controller.line
    if match == None or match_location == None:
        return None
    if mode == "bp":
        process.setBreakpoint(match[0], match[1], debugger, ctx)
        return { "filename": match_location.filename, "line": match_location.line, "id": len(ctx.breakpoints) - 1 }
    else:
        process.setPasspoint(match[0], match[1], debugger, ctx)
        return { "filename": match_location.filename, "line": match_location.line, "id": len(ctx.passpoints) - 1 }
    
def get_typed_value(type: DebugTypeInfo, value, ctx: DebuggingContext) -> str:
    if type.category == TypeCategory.ENUM:
        if value >= 0 and value <= len(type.members):
            return f"{type.name}.{type.members[value]} ({value})"
        return f"{type.name} ({value})"
    elif type.category == TypeCategory.FLAG:
        result = ""
        for index in range(len(type.members)):
            member = type.members[index]
            if ((2 ** index) & value) != 0:
                result += str(member)
        if len(result) > 0:
            result = f"{type.name}.{result} ({value})"
        else:
            return f"{type.name} ({value})"
    elif type.name == "char":
        return chr(value)
    elif type.name == "bool":
        return "true" if value != 0 else "false"
    elif type.name == "state" or type.name == "StateNo":
        if (state := get_state_by_id(value, ctx)) != None:
            return f"State {state.name} ({value})"
        return f"State {value}"
    elif type.name == "target":
        return f"Target ID {value}"
    
    return str(value)

def breakpointsToJson(ctx: DebuggingContext):
    breakpoints = []
    passpoints = []
    index = 0
    for bp in ctx.breakpoints:
        if (state := get_state_by_id(bp[0], ctx)) != None:
            breakpoints.append({ "filename": state.states[bp[1]].filename, "line": state.states[bp[1]].line, "id": index })
        index += 1
    index = 0
    for bp in ctx.passpoints:
        if (state := get_state_by_id(bp[0], ctx)) != None:
            passpoints.append({ "filename": state.states[bp[1]].filename, "line": state.states[bp[1]].line, "id": index })
        index += 1
    return { "breakpoints": breakpoints, "passpoints": passpoints }

def listPlayers(game_address: int, p1_address: int, include_enemy: bool, debugger: DebuggerTarget, ctx: DebuggingContext):
    results: list[dict] = []

    for idx in range(60):
        player_address = process.getValue(game_address + debugger.launch_info.database["player"] + idx * 4, debugger, ctx)
        if player_address == 0:
            continue
        player_exist = process.getValue(player_address + debugger.launch_info.database["exist"], debugger, ctx)
        if player_exist == 0:
            continue
        root_address = process.getValue(player_address + debugger.launch_info.database["root_addr"], debugger, ctx)
        helper_id = process.getValue(player_address + debugger.launch_info.database["helperid"], debugger, ctx)
        if player_address == p1_address or root_address == p1_address or include_enemy:
            player_name = process.getString(player_address + 0x20, debugger, ctx)
            player_type = "Player" if idx < 4 else f"Helper({helper_id})"
            player_team = "p1" if player_address == p1_address or root_address == p1_address else "p2"
            player_id = process.getValue(player_address + 0x04, debugger, ctx)
            results.append({
                "name": f"{player_name} ({player_type}, {player_team})",
                "id": player_id
            })
    
    return results

def getTriggerValue(trigger_name: str, target_address: int, game_address: int, debugger: DebuggerTarget, ctx: DebuggingContext):
    target = trigger_name.lower()
    detailResult = None

    if target in debugger.launch_info.database["triggers"]:
        offset = debugger.launch_info.database["triggers"][target]
        raw_value = process.getValue(target_address + offset[0], debugger, ctx)
        detailResult = {
            "name": trigger_name,
            "value": raw_value
        }
    elif target in debugger.launch_info.database["game_triggers"]:
        trigger_detail = debugger.launch_info.database["game_triggers"][target]
        if trigger_detail[1] == int:
            raw_value = process.getValue(game_address + trigger_detail[0], debugger, ctx)
            detailResult = {
                "name": trigger_name,
                "value": raw_value
            }
        elif trigger_detail[1] == float:
            raw_value = process.getBytes(game_address + trigger_detail[0], debugger, ctx, 4)
            resolved_value = round(struct.unpack('<f', raw_value)[0], 3)
            detailResult = {
                "name": trigger_name,
                "value": resolved_value
            }
        elif trigger_detail[1] == bool:
            raw_value = process.getValue(game_address + trigger_detail[0], debugger, ctx)
            detailResult = {
                "name": trigger_name,
                "value": raw_value != 0
            }
        elif trigger_detail[1] == "double":
            raw_value = process.getBytes(game_address + trigger_detail[0], debugger, ctx, 8)
            resolved_value = round(struct.unpack('<d', raw_value)[0], 3)
            detailResult = {
                "name": trigger_name,
                "value": raw_value
            }
        else:
            ## this is for non-builtin types (e.g. enum/flag) which can be resolved later
            raw_value = process.getValue(game_address + trigger_detail[0], debugger, ctx)
            detailResult = {
                "name": trigger_name,
                "value": raw_value
            }

    return detailResult