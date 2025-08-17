from mtl.utils.func import generate_random_string
from mtl.utils.debug import get_state_by_id
from mtl.types.debugging import *
from mtl.types.shared import DebuggerError
from mtl.debugging.address import SELECT_VERSION_ADDRESS, ADDRESS_DATABASE

import ctypes
import copy
import math
import multiprocessing
from queue import Empty
import time
import threading
import psutil
import shutil
import os
import subprocess
import struct

events_queue = multiprocessing.Queue()
results_queue = multiprocessing.Queue()

## utility function to update the breakpoint list in memory
def setBreakpoint(stateno: int, index: int, target: DebuggerTarget, ctx: DebuggingContext):
    if len(ctx.breakpoints) >= 9:
        print(f"Reached maximum active breakpoint count (9)")
        return
    
    ctx.breakpoints.append((stateno, index))

    ## suspend the thread
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    thread_handle = ctypes.windll.kernel32.OpenThread(THREAD_GET_SET_CONTEXT, 0, target.launch_info.thread_id)
    if target.launch_info.state != DebugProcessState.SUSPENDED_WAIT: _winapi(ctypes.windll.kernel32.SuspendThread(thread_handle), errno = -1)

    ## write the breakpoint list
    start_addr = target.launch_info.database['SCTRL_BREAKPOINT_TABLE']
    for bp in ctx.breakpoints:
        set_addr_int(start_addr, bp[0], process_handle)
        set_addr_int(start_addr + 4, bp[1], process_handle)
        start_addr += 8

    ## resume thread now that breakpoint is applied
    if target.launch_info.state != DebugProcessState.SUSPENDED_WAIT: _winapi(ctypes.windll.kernel32.ResumeThread(thread_handle), errno = -1)

## utility function to read variables from memory
def getVariable(index: int, offset: int, size: int, is_float: bool, target: DebuggerTarget, ctx: DebuggingContext) -> float:
    if ctx.current_owner == 0:
        print(f"Cannot get variables when the current owner is not known!")
        return 0

    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    
    if is_float:
        variable_value = get_uncached(ctx.current_owner + target.launch_info.database["fvar"] + index * 4, process_handle)
        return round(struct.unpack('<f', variable_value.to_bytes(4, byteorder = 'little'))[0], 3)
    else:
        variable_value = get_uncached(ctx.current_owner + target.launch_info.database["var"] + index * 4, process_handle)
        start_pow2 = 2 ** offset
        end_pow2 = 2 ** (offset + size)
        mask = ctypes.c_int32(end_pow2 - start_pow2)
        end_mask = (2 ** size) - 1
        value = ((variable_value & mask.value) >> offset) & end_mask
        if size == 32:
            return ctypes.c_int32(value).value
        elif size == 16:
            return ctypes.c_short(value).value
        elif size == 8:
            return ctypes.c_byte(value).value
        return value
    
## utility function to read trigger values from memory
def getValue(offset: int, target: DebuggerTarget, ctx: DebuggingContext) -> int:
    if ctx.current_owner == 0:
        print(f"Cannot get trigger values when the current owner is not known!")
        return 0

    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    return get_uncached(ctx.current_owner + offset, process_handle)

## helper to get a value from cache if possible.
def get_cached(addr: int, handle: int, launch_info: DebuggerLaunchInfo) -> int:
    if addr in launch_info.cache: return launch_info.cache[addr]
    buf = ctypes.create_string_buffer(4)
    read = c_int()
    _winapi(ctypes.windll.kernel32.ReadProcessMemory(handle, addr, buf, 4, ctypes.byref(read)))
    launch_info.cache[addr] = int.from_bytes(buf, byteorder='little')
    return launch_info.cache[addr]

## helper to get a value without caching (for values which change e.g. stateno)
def get_uncached(addr: int, handle: int) -> int:
    buf = ctypes.create_string_buffer(4)
    read = c_int()
    _winapi(ctypes.windll.kernel32.ReadProcessMemory(handle, addr, buf, 4, ctypes.byref(read)))
    return int.from_bytes(buf, byteorder='little')

def set_addr(addr: int, val: int, handle: int):
    v = val.to_bytes(1, byteorder='little', signed=False)
    buf = ctypes.create_string_buffer(v, 1)

    total = c_int()
    _winapi(ctypes.windll.kernel32.WriteProcessMemory(handle, addr, buf, 1, ctypes.byref(total)))

def set_addr_int(addr: int, val: int, handle: int):
    v = val.to_bytes(4, byteorder='little', signed=False)
    buf = ctypes.create_string_buffer(v, 4)

    total = c_int()
    _winapi(ctypes.windll.kernel32.WriteProcessMemory(handle, addr, buf, 4, ctypes.byref(total)))

## for us we only care about DEBUG_REGISTERS and INTEGER
def get_context(handle: int, context: CONTEXT):
    context.ContextFlags = CONTEXT_DEBUG_REGISTERS | CONTEXT_INTEGER | CONTEXT_CONTROL
    _winapi(ctypes.windll.kernel32.Wow64GetThreadContext(handle, ctypes.byref(context)))
def set_context(handle: int, context: CONTEXT):
    _winapi(ctypes.windll.kernel32.Wow64SetThreadContext(handle, ctypes.byref(context)))
def resume(handle: int, context: CONTEXT):
    # set RF flag before resume
    get_context(handle, context)
    context.EFlags |= RESUME_FLAG
    set_context(handle, context)

## helper function to check a winapi result and call GetLastError if it failed.
def _winapi(result: int, errno: int = 0):
    if result == errno:
        err = ctypes.windll.kernel32.GetLastError()
        raise DebuggerError(f"Failed to run win32 API call: call failed with error code {err}.")
## similar to _winapi, but does not raise an error.
def _winapi_check(result: int) -> int:
    if result == 0:
        err = ctypes.windll.kernel32.GetLastError()
        return err
    return 0

## waits for the subprocess to exit, then cleans up the copied character folder.
def _wait_mugen(target: DebuggerTarget, folder: str):
    while target.subprocess.poll() == None:
        time.sleep(1/60)
    # delay cleanup to make sure MUGEN shutdown is completed.
    target.launch_info.state = DebugProcessState.EXIT
    time.sleep(1)
    if folder != None:
        shutil.rmtree(folder)

def _debug_mugen(launch_info: DebuggerLaunchInfo, events: multiprocessing.Queue, results: multiprocessing.Queue):
    ## insert self as a debugger into the target process, then indicate the process can unsuspend
    _winapi(ctypes.windll.kernel32.DebugActiveProcess(launch_info.process_id))
    launch_info.state = DebugProcessState.SUSPENDED_PROCEED

    process_handle = None
    thread_handle = None
    step_break = False

    event = DEBUG_EVENT()
    context = CONTEXT()
    while launch_info.state != DebugProcessState.EXIT:
        ## for each debug event, we push it to the `events` queue, wait for the debugger to handle it,
        ## and then continue the process.
        if (checked := _winapi_check(ctypes.windll.kernel32.WaitForDebugEvent(ctypes.byref(event), math.floor(1000/60)))) != 0:
            if checked == 121:
                ## timeout waiting for event, just re-run. this ensures it will exit when needed as well.
                continue
            raise DebuggerError(f"Failed to run win32 API call: call failed with error code {checked}.")
        
        if event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT:
            ## store the thread ID
            launch_info.thread_id = event.dwThreadId
            process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, event.dwProcessId)
            thread_handle = ctypes.windll.kernel32.OpenThread(THREAD_GET_SET_CONTEXT, 0, event.dwThreadId)

        if event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
            ## EXCEPTION_DEBUG_EVENT is used for user breakpoints.
            record = event.u.Exception.ExceptionRecord
            if record.ExceptionCode in [STATUS_WX86_BREAKPOINT, STATUS_WX86_SINGLE_STEP, STATUS_BREAKPOINT, STATUS_SINGLE_STEP]:
                ## submit the event to the handler. handler will check the address is correct.
                events.put(DebugBreakEvent(record.ExceptionAddress, step_break))
                ## block until the result is received.
                result: DebugBreakResult = results.get()
                step_break = result.step
            else:
                raise Exception(f"unhandled exception code: {record.ExceptionCode}")

        try:
            if thread_handle != None:
                resume(thread_handle, context)
            _winapi(ctypes.windll.kernel32.ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE))
        except DebuggerError:
            ## this may happen if the target process dies.
            launch_info.state = DebugProcessState.EXIT

def check_breakpoints(player: int, event: DebugBreakEvent, thread_handle: int, process_handle: int, context: CONTEXT, breakpoints: list[tuple[int, int]], launch_info: DebuggerLaunchInfo, ctx: DebuggingContext) -> Optional[tuple[int, int]]:
    ## now need to detect if the current state+controller are a target for a breakpoint
    get_context(thread_handle, context)
    # check the player address matches
    game_address = get_cached(launch_info.database["game"], process_handle, launch_info)
    player_address = get_cached(game_address + launch_info.database["player"] + player * 4, process_handle, launch_info)
    ## check if the read player address matches Ebp
    if player_address != context.Ebp:
        return None
    
    ## now check if the player either is p1, or is owned by p1
    p1_address = get_cached(game_address + launch_info.database["player"], process_handle, launch_info)
    if player_address != p1_address:
        root_address = get_uncached(player_address + 0x1650, process_handle)
        if root_address != p1_address:
            return None

    ## player either is p1, or is owned by p1.
    with_step = copy.deepcopy(breakpoints)
    if event.step:
        with_step.insert(0, (get_uncached(player_address + launch_info.database["stateno"], process_handle), ctx.last_index))
    
    for bp in with_step:
        ## controller index was stored by the other breakpoint handler
        if bp[1] != ctx.last_index:
            continue
        ## stateno comes from player structure
        if bp[0] != get_uncached(player_address + launch_info.database["stateno"], process_handle):
            continue
        ## breakpoint was matched, pause and wait for input
        launch_info.state = DebugProcessState.PAUSED
        ctx.current_breakpoint = bp
        ctx.current_owner = player_address
        ## find the file and line corresponding to this breakpoint
        if (state := get_state_by_id(bp[0], ctx)) == None:
            print(f"Warning: Debugger could not find any state with ID {bp[0]} in database.")
            return bp
        if bp[1] >= len(state.states):
            print(f"Warning: Debugger could not match controller index {bp[1]} for state {bp[0]} in database.")
            return bp
        player_id = get_uncached(player_address + 0x04, process_handle)
        helper_id = get_uncached(player_address + 0x1644, process_handle)
        player_name = "root" if player_address == p1_address else f"helper({helper_id})"
        print(f"Encountered breakpoint for player {player_id} ( {player_name} ) at: {state.states[bp[1]]} (state {bp[0]}, controller {bp[1]})")
        return bp
    return None

def _debug_handler(launch_info: DebuggerLaunchInfo, events: multiprocessing.Queue, results: multiprocessing.Queue, ctx: DebuggingContext):
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, launch_info.process_id)

    ## wait for the initial `suspended` states to progress
    while launch_info.state in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT]:
        time.sleep(1/10000)
        continue

    ## identify the address database to use
    version_address = get_cached(SELECT_VERSION_ADDRESS, process_handle, launch_info)
    launch_info.database = ADDRESS_DATABASE[version_address]

    ## get thread handle and suspend the thread temporarily
    thread_handle = ctypes.windll.kernel32.OpenThread(THREAD_GET_SET_CONTEXT, 0, launch_info.thread_id)
    _winapi(ctypes.windll.kernel32.SuspendThread(thread_handle), errno = -1)

    ## write the breakpoint dispatch handling table with initial values, 0xFF
    for idx in range(launch_info.database['SCTRL_BREAKPOINT_FUNC_ADDR'] - launch_info.database['SCTRL_BREAKPOINT_TABLE']):
        set_addr(launch_info.database['SCTRL_BREAKPOINT_TABLE'] + idx, 0xFF, process_handle)

    ## write the breakpoint handling function
    for idx in range(len(launch_info.database['SCTRL_BREAKPOINT_FUNC'])):
        set_addr(launch_info.database['SCTRL_BREAKPOINT_FUNC_ADDR'] + idx, launch_info.database['SCTRL_BREAKPOINT_FUNC'][idx], process_handle)

    ## write the breakpoint handling jump
    for idx in range(len(launch_info.database['SCTRL_BREAKPOINT_INSERT_FUNC'])):
        set_addr(launch_info.database['SCTRL_BREAKPOINT_INSERT'] + idx, launch_info.database['SCTRL_BREAKPOINT_INSERT_FUNC'][idx], process_handle)

    ## now add a breakpoint at the breakpoint insertion address
    context = CONTEXT()
    get_context(thread_handle, context)

    context.Dr0 = launch_info.database["SCTRL_BREAKPOINT_ADDR"]
    ## TODO: support passpoints again.
    context.Dr1 = launch_info.database["SCTRL_BREAKPOINT_ADDR"] # launch_info.database["SCTRL_PASSPOINT_ADDR"]
    context.Dr7 |= 0x103 | 0x0C # bits 0, 1, 2, 3, 8 enable breakpoint set on DR0 and DR1.

    set_context(thread_handle, context)

    ## resume thread now that breakpoint is applied
    _winapi(ctypes.windll.kernel32.ResumeThread(thread_handle), errno = -1)

    while launch_info.state != DebugProcessState.EXIT:
        try:
            ## this can be blocked indefinitely if we allow infinite timeout.
            ## set timeout to a small number so it can continue if nothing arrives
            ## (it would be better to be infinite but then this thread never exits)
            next_event: DebugBreakEvent = events.get(True, 1/60)
            if next_event.address == launch_info.database["SCTRL_PASSPOINT_ADDR"]:
                ## early exit: if we have no breakpoints, nothing to worry about
                if len(ctx.passpoints) == 0:
                    results.put(DebugBreakResult(step = next_event.step))
                    continue

                # check p1 first, then check each Helper
                next_bp = check_breakpoints(0, next_event, thread_handle, process_handle, context, ctx.passpoints, launch_info, ctx)
                if next_bp == None:
                    for index in range(4, 60):
                        next_bp = check_breakpoints(index, next_event, thread_handle, process_handle, context, ctx.passpoints, launch_info, ctx)
                        if next_bp != None: break
                
                if launch_info.state != DebugProcessState.PAUSED:
                    results.put(DebugBreakResult())
            elif next_event.address == launch_info.database["SCTRL_BREAKPOINT_ADDR"]:
                ## early exit: if we have no breakpoints, nothing to worry about
                if len(ctx.breakpoints) == 0 and len(ctx.passpoints) == 0:
                    results.put(DebugBreakResult(step = next_event.step))
                    continue

                ## always store ECX for passpoints
                get_context(thread_handle, context)
                ctx.last_index = context.Ecx

                ## early-exit again after storing ECX
                if len(ctx.breakpoints) == 0:
                    results.put(DebugBreakResult(step = next_event.step))
                    continue
                
                # check p1 first, then check each Helper
                next_bp = check_breakpoints(0, next_event, thread_handle, process_handle, context, ctx.breakpoints, launch_info, ctx)
                if next_bp == None:
                    for index in range(4, 60):
                        next_bp = check_breakpoints(index, next_event, thread_handle, process_handle, context, ctx.breakpoints, launch_info, ctx)
                        if next_bp != None: break

                ## no breakpoint matched, resume
                if launch_info.state != DebugProcessState.PAUSED:
                    results.put(DebugBreakResult())
            else:
                ## just immediately tell the engine to continue in this case.
                results.put(DebugBreakResult(step = next_event.step))
        except Empty as exc:
            ## this happens if the queue is empty and the read times out.
            continue

def launch(target: str, character: str, ctx: DebuggingContext) -> DebuggerTarget:
    ## copy the character folder to the MUGEN chars folder.
    working = os.path.dirname(os.path.abspath(target))
    chara = os.path.dirname(os.path.abspath(character))
    character_folder = None
    if chara != f"{working}/chars":
        random_id = generate_random_string(8)
        shutil.copytree(chara, f"{working}/chars/{random_id}/")
        character = f"chars/{random_id}/{os.path.basename(character)}"
        print(f"Relocated character data to {character} for launch.")
        character_folder = os.path.dirname(f"{working}/{character}")

    ## prep the command-line arguments.
    args = [target, "-p1", character, "-p2", "kfm", "-p1.ai", "0", "-p2.ai", "0"]
    child = subprocess.Popen(args, cwd=working, creationflags=CREATE_SUSPENDED)

    ## share the launch info across processes
    launch_info = DebuggerLaunchInfo(child.pid, 0, {}, character_folder, DebugProcessState.SUSPENDED_WAIT, {})
    result = DebuggerTarget(child, launch_info)

    ## dispatch a thread to check when the subprocess closes + clean up automatically.
    threading.Thread(target=_wait_mugen, args=(result, character_folder)).start()

    ## dispatch a thread to handle debugging events from the target process
    threading.Thread(target=_debug_mugen, args=(launch_info, events_queue, results_queue)).start()

    ## dispatch a thread to read events processed by debugger and push them back to the debugger
    threading.Thread(target=_debug_handler, args=(launch_info, events_queue, results_queue, ctx)).start()

    print(f"Launched MUGEN suspended process. Type `continue` to continue.")

    return result

def cont(target: DebuggerTarget, step: bool = False):
    if target.subprocess != None and target.launch_info.state == DebugProcessState.SUSPENDED_PROCEED:
        # resume the process, 
        psutil.Process(target.subprocess.pid).resume()
        target.launch_info.state = DebugProcessState.RUNNING
    elif target.subprocess != None and target.launch_info.state == DebugProcessState.PAUSED:
        results_queue.put(DebugBreakResult(step = step))
        target.launch_info.state = DebugProcessState.RUNNING