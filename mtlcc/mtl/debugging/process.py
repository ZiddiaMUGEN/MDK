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
import json

from mtl.debugging.commands import sendResponseIPC

events_queue = multiprocessing.Queue()
results_queue = multiprocessing.Queue()

def suspendExternal(target: DebuggerTarget):
    thread_handle = ctypes.windll.kernel32.OpenThread(THREAD_GET_SET_CONTEXT, 0, target.launch_info.thread_id)
    _winapi(ctypes.windll.kernel32.SuspendThread(thread_handle), errno = -1)

def resumeExternal(target: DebuggerTarget):
    thread_handle = ctypes.windll.kernel32.OpenThread(THREAD_GET_SET_CONTEXT, 0, target.launch_info.thread_id)
    if target.launch_info.state != DebugProcessState.SUSPENDED_WAIT: _winapi(ctypes.windll.kernel32.ResumeThread(thread_handle), errno = -1)

## utility function to update the breakpoint list in memory
def setBreakpoint(stateno: int, index: int, target: DebuggerTarget, ctx: DebuggingContext):
    if len(ctx.breakpoints) >= 8:
        if not ctx.quiet: print(f"Reached maximum active breakpoint count (8)")
        return
    
    ctx.breakpoints.append((stateno, index))

    ## update breakpoint table
    insertBreakpointTable(ctx.breakpoints, ctx.passpoints, target, ctx)

def setPasspoint(stateno: int, index: int, target: DebuggerTarget, ctx: DebuggingContext):
    if len(ctx.passpoints) >= 8:
        if not ctx.quiet: print(f"Reached maximum active passpoint count (8)")
        return
    
    ctx.passpoints.append((stateno, index))

    ## update breakpoint table
    insertBreakpointTable(ctx.breakpoints, ctx.passpoints, target, ctx)

def insertBreakpointTable(breakpoints: list[tuple[int, int]], passpoints: list[tuple[int, int]], target: DebuggerTarget, ctx: DebuggingContext):
    ## suspend the thread
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    thread_handle = ctypes.windll.kernel32.OpenThread(THREAD_GET_SET_CONTEXT, 0, target.launch_info.thread_id)
    if target.launch_info.state != DebugProcessState.SUSPENDED_WAIT: _winapi(ctypes.windll.kernel32.SuspendThread(thread_handle), errno = -1)

    ## re-fill the breakpoint list with 0xFF
    for idx in range(target.launch_info.database['SCTRL_BREAKPOINT_FUNC_ADDR'] - target.launch_info.database['SCTRL_BREAKPOINT_TABLE']):
        set_addr(target.launch_info.database['SCTRL_BREAKPOINT_TABLE'] + idx, 0xFF, process_handle, target.launch_info, ctx)

    ## write the breakpoint list
    start_addr = target.launch_info.database['SCTRL_BREAKPOINT_TABLE']
    breakpoints_ = copy.deepcopy(breakpoints)
    for bp in breakpoints_:
        set_addr_int(start_addr, bp[0], process_handle, target.launch_info, ctx)
        set_addr_int(start_addr + 4, bp[1], process_handle, target.launch_info, ctx)
        start_addr += 8

    start_addr = target.launch_info.database['SCTRL_BREAKPOINT_TABLE'] + (8 * 10)
    for bp in passpoints:
        set_addr_int(start_addr, bp[0], process_handle, target.launch_info, ctx)
        set_addr_int(start_addr + 4, bp[1], process_handle, target.launch_info, ctx)
        start_addr += 8

    ## resume thread now that breakpoint is applied
    if target.launch_info.state != DebugProcessState.SUSPENDED_WAIT: _winapi(ctypes.windll.kernel32.ResumeThread(thread_handle), errno = -1)

## utility function to read variables from memory
def getVariable(base_addr: int, index: int, offset: int, size: int, is_float: bool, is_system: bool, target: DebuggerTarget, ctx: DebuggingContext) -> float:
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    
    if is_float:
        if is_system:
            variable_value = get_uncached(base_addr + target.launch_info.database["sysfvar"] + index * 4, process_handle)
        else:
            variable_value = get_uncached(base_addr + target.launch_info.database["fvar"] + index * 4, process_handle)
        return round(struct.unpack('<f', variable_value.to_bytes(4, byteorder = 'little'))[0], 3)
    else:
        if is_system:
            variable_value = get_uncached(base_addr + target.launch_info.database["sysvar"] + index * 4, process_handle)
        else:
            variable_value = get_uncached(base_addr + target.launch_info.database["var"] + index * 4, process_handle)
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
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    return get_uncached(offset, process_handle)

## utility function to read trigger values from memory
def getBytes(offset: int, target: DebuggerTarget, ctx: DebuggingContext, count: int) -> bytes:
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    return get_bytes(offset, process_handle, count)

## utility function to read strings from memory
def getString(offset: int, target: DebuggerTarget, ctx: DebuggingContext) -> str:
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    result = ""
    while (b := get_byte(offset, process_handle)) != b'':
        result += b.decode("utf-8")
        offset += 1
    return result

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

def get_byte(addr: int, handle: int) -> bytes:
    buf = ctypes.create_string_buffer(1)
    read = c_int()
    _winapi(ctypes.windll.kernel32.ReadProcessMemory(handle, addr, buf, 1, ctypes.byref(read)))
    return buf.value

def get_bytes(addr: int, handle: int, count: int) -> bytes:
    buf = ctypes.create_string_buffer(count)
    read = c_int()
    _winapi(ctypes.windll.kernel32.ReadProcessMemory(handle, addr, buf, count, ctypes.byref(read)))
    return buf.value

def set_addr(addr: int, val: int, handle: int, launch_info: DebuggerLaunchInfo, ctx: DebuggingContext):
    unprotect(launch_info, ctx)

    v = val.to_bytes(1, byteorder='little', signed=False)
    buf = ctypes.create_string_buffer(v, 1)

    total = c_int()
    _winapi(ctypes.windll.kernel32.WriteProcessMemory(handle, addr, buf, 1, ctypes.byref(total)))

def set_addr_int(addr: int, val: int, handle: int, launch_info: DebuggerLaunchInfo, ctx: DebuggingContext):
    unprotect(launch_info, ctx)

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
    # in IPC mode, send IPC command to the adapter to inform it of exit
    if folder != None:
        shutil.rmtree(folder)
    if target.launch_info.ipc:
        retval = target.subprocess.poll()
        if retval not in [0, 1]:
            sendResponseIPC(DebuggerResponseIPC(b'00000000-0000-0000-0000-000000000000', DebuggerCommand.IPC_EXIT, DebuggerResponseType.ERROR, json.dumps({ "ret": retval }).encode('utf-8')))
        else:
            sendResponseIPC(DebuggerResponseIPC(b'00000000-0000-0000-0000-000000000000', DebuggerCommand.IPC_EXIT, DebuggerResponseType.SUCCESS, json.dumps({ "ret": retval }).encode('utf-8')))

def _debug_mugen(launch_info: DebuggerLaunchInfo, events: multiprocessing.Queue, results: multiprocessing.Queue):
    ## insert self as a debugger into the target process, then indicate the process can unsuspend
    _winapi(ctypes.windll.kernel32.DebugActiveProcess(launch_info.process_id))
    launch_info.state = DebugProcessState.SUSPENDED_PROCEED

    process_handle = None
    thread_handle = None

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
                events.put(DebugBreakEvent(record.ExceptionAddress))
                ## block until the result is received.
                result: DebugBreakResult = results.get()
            else:
                raise Exception(f"unhandled exception code: {record.ExceptionCode}")

        try:
            if thread_handle != None:
                resume(thread_handle, context)
            _winapi(ctypes.windll.kernel32.ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE))
        except DebuggerError:
            ## this may happen if the target process dies.
            launch_info.state = DebugProcessState.EXIT

def _debug_handler(launch_info: DebuggerLaunchInfo, events: multiprocessing.Queue, results: multiprocessing.Queue, ctx: DebuggingContext):
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, launch_info.process_id)

    ## identify the address database to use
    version_address = get_cached(SELECT_VERSION_ADDRESS, process_handle, launch_info)
    launch_info.database = ADDRESS_DATABASE[version_address]

    ## for winmugen, we need to change protection on the page for the breakpoint functions.
    ## this is because winmugen has less room for the function in .text than other versions,
    ## so the function is placed in rdata instead.
    if version_address == 0x5002E0C1:
        ctx.is_winmugen = True

    ## wait for the initial `suspended` states to progress
    while launch_info.state in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT]:
        time.sleep(1/10000)
        continue

    ## early exit from IPC (without running any code)
    if launch_info.state == DebugProcessState.EXIT:
        return

    ## get thread handle and suspend the thread temporarily
    thread_handle = ctypes.windll.kernel32.OpenThread(THREAD_GET_SET_CONTEXT, 0, launch_info.thread_id)
    _winapi(ctypes.windll.kernel32.SuspendThread(thread_handle), errno = -1)

    ## write the breakpoint dispatch handling table with initial values, 0xFF
    for idx in range(launch_info.database['SCTRL_BREAKPOINT_FUNC_ADDR'] - launch_info.database['SCTRL_BREAKPOINT_TABLE']):
        set_addr(launch_info.database['SCTRL_BREAKPOINT_TABLE'] + idx, 0xFF, process_handle, launch_info, ctx)

    ## write the breakpoint handling function
    for idx in range(len(launch_info.database['SCTRL_BREAKPOINT_FUNC'])):
        set_addr(launch_info.database['SCTRL_BREAKPOINT_FUNC_ADDR'] + idx, launch_info.database['SCTRL_BREAKPOINT_FUNC'][idx], process_handle, launch_info, ctx)

    ## write the passpoint handling function
    for idx in range(len(launch_info.database['SCTRL_PASSPOINT_FUNC'])):
        set_addr(launch_info.database['SCTRL_PASSPOINT_FUNC_ADDR'] + idx, launch_info.database['SCTRL_PASSPOINT_FUNC'][idx], process_handle, launch_info, ctx)

    ## write the breakpoint handling jump
    for idx in range(len(launch_info.database['SCTRL_BREAKPOINT_INSERT_FUNC'])):
        set_addr(launch_info.database['SCTRL_BREAKPOINT_INSERT'] + idx, launch_info.database['SCTRL_BREAKPOINT_INSERT_FUNC'][idx], process_handle, launch_info, ctx)

    ## write the passpoint handling jump
    for idx in range(len(launch_info.database['SCTRL_PASSPOINT_INSERT_FUNC'])):
        set_addr(launch_info.database['SCTRL_PASSPOINT_INSERT'] + idx, launch_info.database['SCTRL_PASSPOINT_INSERT_FUNC'][idx], process_handle, launch_info, ctx)

    ## restore the breakpoint list from input
    start_addr = launch_info.database['SCTRL_BREAKPOINT_TABLE']
    breakpoints_ = copy.deepcopy(ctx.breakpoints)
    for bp in breakpoints_:
        set_addr_int(start_addr, bp[0], process_handle, launch_info, ctx)
        set_addr_int(start_addr + 4, bp[1], process_handle, launch_info, ctx)
        start_addr += 8

    start_addr = launch_info.database['SCTRL_BREAKPOINT_TABLE'] + (8 * 10)
    for bp in ctx.passpoints:
        set_addr_int(start_addr, bp[0], process_handle, launch_info, ctx)
        set_addr_int(start_addr + 4, bp[1], process_handle, launch_info, ctx)
        start_addr += 8

    ## now add a breakpoint at the breakpoint insertion address
    context = CONTEXT()
    get_context(thread_handle, context)

    context.Dr0 = launch_info.database["SCTRL_BREAKPOINT_ADDR"]
    context.Dr1 = launch_info.database["SCTRL_PASSPOINT_ADDR"]
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
                ## always store breakpoint info for passpoints
                get_context(thread_handle, context)
                ctx.current_owner = context.Ebp
                if ctx.is_winmugen:
                    ctx.current_owner = context.Esi
                ctx.last_index = get_uncached(ctx.current_owner + 0x5c, process_handle)

                ## set the owner's address into the passpoint-step address
                is_step = ctx.current_owner == get_uncached(launch_info.database["SCTRL_STEP_ADDR"] + 4, process_handle)
                set_addr_int(launch_info.database["SCTRL_STEP_ADDR"] + 4, ctx.current_owner, process_handle, launch_info, ctx)
                
                match_breakpoint(launch_info, ctx, process_handle, is_step)
            elif next_event.address == launch_info.database["SCTRL_BREAKPOINT_ADDR"]:
                ## always store breakpoint info for passpoints
                get_context(thread_handle, context)
                ctx.last_index = context.Ecx
                ctx.current_owner = context.Ebp
                if ctx.is_winmugen:
                    ctx.current_owner = context.Esi

                ## set the owner's address into the breakpoint-step address
                is_step = ctx.current_owner == get_uncached(launch_info.database["SCTRL_STEP_ADDR"], process_handle)
                set_addr_int(launch_info.database["SCTRL_STEP_ADDR"], ctx.current_owner, process_handle, launch_info, ctx)
                
                match_breakpoint(launch_info, ctx, process_handle, is_step)
            else:
                ## just immediately tell the engine to continue in this case.
                results.put(DebugBreakResult())
        except Empty as exc:
            ## this happens if the queue is empty and the read times out.
            continue

def match_breakpoint(launch_info: DebuggerLaunchInfo, ctx: DebuggingContext, process_handle: int, is_step: bool = False):
    ## breakpoint was matched, pause and wait for input
    launch_info.state = DebugProcessState.PAUSED
    stateno = get_uncached(ctx.current_owner + launch_info.database["stateno"], process_handle)
    ctx.current_breakpoint = (stateno, ctx.last_index)
    ## in IPC mode, notify the adapter that the breakpoint was reached
    if launch_info.ipc:
        ## find the file and line corresponding to this breakpoint
        if (state := get_state_by_id(stateno, ctx)) == None:
            return
        if ctx.last_index >= len(state.states):
            return
        player_id = get_uncached(ctx.current_owner + 0x04, process_handle)
        sendResponseIPC(DebuggerResponseIPC(
            b'00000000-0000-0000-0000-000000000000', DebuggerCommand.IPC_STEP if is_step else DebuggerCommand.IPC_HIT_BREAKPOINT, DebuggerResponseType.SUCCESS, 
            json.dumps({ "filename": state.states[ctx.last_index].filename, "line": state.states[ctx.last_index].line, "owner": player_id }).encode('utf-8')
        ))
    else:
        ## find the file and line corresponding to this breakpoint
        if (state := get_state_by_id(stateno, ctx)) == None:
            if not ctx.quiet: print(f"Warning: Debugger could not find any state with ID {stateno} in database.")
            return
        if ctx.last_index >= len(state.states):
            if not ctx.quiet: print(f"Warning: Debugger could not match controller index {ctx.last_index} for state {stateno} in database.")
            return
        player_id = get_uncached(ctx.current_owner + 0x04, process_handle)
        helper_id = get_uncached(ctx.current_owner + launch_info.database["helperid"], process_handle)
        game_address = get_cached(launch_info.database["game"], process_handle, launch_info)
        p1_address = get_cached(game_address + launch_info.database["player"], process_handle, launch_info)
        player_name = "root" if ctx.current_owner == p1_address else f"helper({helper_id})"
        if not ctx.quiet: 
            if not is_step:
                print(f"Encountered breakpoint for player {player_id} ( {player_name} ) at: {state.states[ctx.last_index]} (state {stateno}, controller {ctx.last_index})")
            else:
                print(f"Step to {state.states[ctx.last_index]} (state {stateno}, controller {ctx.last_index})")

def launch(target: str, character: str, ctx: DebuggingContext) -> DebuggerTarget:
    ## copy the character folder to the MUGEN chars folder.
    working = os.path.dirname(os.path.abspath(target))
    chara = os.path.dirname(os.path.abspath(character))
    character_folder = None
    if chara != f"{working}/chars":
        random_id = generate_random_string(8)
        shutil.copytree(chara, f"{working}/chars/{random_id}/")
        character = f"chars/{random_id}/{os.path.basename(character)}"
        if not ctx.quiet: print(f"Relocated character data to {character} for launch.")
        character_folder = os.path.dirname(f"{working}/{character}")

    ## prep the command-line arguments.
    args = [target, "-p1", character, "-p2", ctx.p2_target, "-p1.ai", str(ctx.enable_ai), "-p2.ai", str(ctx.enable_ai)]
    child = subprocess.Popen(args, cwd=working, creationflags=CREATE_SUSPENDED)

    ## share the launch info across processes
    launch_info = DebuggerLaunchInfo(child.pid, 0, {}, character_folder, DebugProcessState.SUSPENDED_WAIT, {}, False)
    result = DebuggerTarget(child, launch_info)

    ## dispatch a thread to check when the subprocess closes + clean up automatically.
    threading.Thread(target=_wait_mugen, args=(result, character_folder)).start()

    ## dispatch a thread to handle debugging events from the target process
    threading.Thread(target=_debug_mugen, args=(launch_info, events_queue, results_queue)).start()

    ## dispatch a thread to read events processed by debugger and push them back to the debugger
    threading.Thread(target=_debug_handler, args=(launch_info, events_queue, results_queue, ctx)).start()

    if not ctx.quiet: print(f"Launched MUGEN suspended process. Type `continue` to continue.")

    return result

def cont(target: DebuggerTarget, ctx: DebuggingContext, next_state = DebugProcessState.RUNNING):
    if target.subprocess != None and target.launch_info.state == DebugProcessState.SUSPENDED_PROCEED:
        # resume the process
        psutil.Process(target.subprocess.pid).resume()
        target.launch_info.state = next_state
    elif target.subprocess != None and target.launch_info.state == DebugProcessState.SUSPENDED_DEBUG:
        # unsuspend directly from the OS (since SUSPENDED_DEBUG happens on a manual break)
        resumeExternal(target)
        target.launch_info.state = next_state
    elif target.subprocess != None and target.launch_info.state == DebugProcessState.PAUSED:
        ## reinsert the breakpoint table
        insertBreakpointTable(ctx.breakpoints, ctx.passpoints, target, ctx)

        results_queue.put(DebugBreakResult())
        target.launch_info.state = next_state

def removeStep(target: DebuggerTarget, ctx: DebuggingContext):
    ## remove all step addresses
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    set_addr_int(target.launch_info.database["SCTRL_STEP_ADDR"], 0, process_handle, target.launch_info, ctx)
    set_addr_int(target.launch_info.database["SCTRL_STEP_ADDR"] + 4, 0, process_handle, target.launch_info, ctx)

def setStep(target: DebuggerTarget, ctx: DebuggingContext, addr: int):
    ## set the owner's address into the breakpoint-step address
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, target.launch_info.process_id)
    ## don't set if this is already marked as the step character.
    if get_uncached(target.launch_info.database["SCTRL_STEP_ADDR"], process_handle) == addr or get_uncached(target.launch_info.database["SCTRL_STEP_ADDR"] + 4, process_handle) == addr:
        return
    set_addr_int(target.launch_info.database["SCTRL_STEP_ADDR"], addr, process_handle, target.launch_info, ctx)
    #set_addr_int(target.launch_info.database["SCTRL_STEP_ADDR"] + 4, addr, process_handle)

def unprotect(launch_info: DebuggerLaunchInfo, ctx: DebuggingContext):
    if ctx.is_winmugen:
        process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, launch_info.process_id)
        read = c_int()
        _winapi(ctypes.windll.kernel32.VirtualProtectEx(process_handle, launch_info.database['SCTRL_BREAKPOINT_TABLE'], 0x2000, 0x40, ctypes.byref(read)))