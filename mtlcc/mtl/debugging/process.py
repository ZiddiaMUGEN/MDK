from mtl.utils.func import generate_random_string
from mtl.types.debugging import *
from mtl.types.shared import DebuggerError
from mtl.debugging.address import SELECT_VERSION_ADDRESS, ADDRESS_DATABASE

import ctypes
import math
import multiprocessing
import time
import threading
import psutil
import shutil
import os
import subprocess

events_queue = multiprocessing.Queue()
results_queue = multiprocessing.Queue()

## helper function to check a winapi result and call GetLastError if it failed.
def _winapi(result: int):
    if result == 0:
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
    if folder != None:
        print(f"Cleaning up copied character data under {folder}.")
        shutil.rmtree(folder)
    target.launch_info.state = DebugProcessState.EXIT

def _debug_mugen(launch_info: DebuggerLaunchInfo, events: multiprocessing.Queue, results: multiprocessing.Queue):
    ## insert self as a debugger into the target process, then indicate the process can unsuspend
    _winapi(ctypes.windll.kernel32.DebugActiveProcess(launch_info.process_id))
    launch_info.state = DebugProcessState.SUSPENDED_PROCEED
    event = DEBUG_EVENT()
    while launch_info.state != DebugProcessState.EXIT:
        ## for each debug event, we push it to the `events` queue, wait for the debugger to handle it,
        ## and then continue the process.
        if (checked := _winapi_check(ctypes.windll.kernel32.WaitForDebugEvent(ctypes.byref(event), math.floor(1000/60)))) != 0:
            if checked == 121:
                ## timeout waiting for event, just re-run. this ensures it will exit when needed as well.
                continue
            raise DebuggerError(f"Failed to run win32 API call: call failed with error code {checked}.")
        if event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT:
            ## EXCEPTION_DEBUG_EVENT is used for user breakpoints.
            record = event.u.Exception.ExceptionRecord
            if record.ExceptionCode in [STATUS_WX86_BREAKPOINT, STATUS_BREAKPOINT]:
                ## submit the event to the handler. handler will check the address is correct.
                events.put(DebugBreakEvent(record.ExceptionAddress))
                result: DebugBreakResult = results.get()

        _winapi(ctypes.windll.kernel32.ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE))

def _debug_handler(launch_info: DebuggerLaunchInfo, events: multiprocessing.Queue, results: multiprocessing.Queue):
    process_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, 0, launch_info.process_id)
    
    ## wait for the initial `suspended` states to progress
    while launch_info.state in [DebugProcessState.SUSPENDED_PROCEED, DebugProcessState.SUSPENDED_WAIT]:
        time.sleep(1/10000)
        continue

    ## identify the address database to use
    buf = ctypes.create_string_buffer(4)
    read = c_int()
    _winapi(ctypes.windll.kernel32.ReadProcessMemory(process_handle, SELECT_VERSION_ADDRESS, buf, 4, ctypes.byref(read)))
    database = ADDRESS_DATABASE[int.from_bytes(buf, byteorder='little')]

    while launch_info.state != DebugProcessState.EXIT:
        try:
            ## this can be blocked indefinitely if we allow infinite timeout.
            ## set timeout to a small number so it can continue if nothing arrives
            ## (it would be better to be infinite but then this thread never exits)
            next_event: DebugBreakEvent = events.get(True, 1/60)
            print(f"Breakpoint hit at address {next_event.address}")
            launch_info.state = DebugProcessState.PAUSED
        except Exception:
            continue

def launch(target: str, character: str) -> DebuggerTarget:
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
    args = [target, "-p1", character, "-p2", "kfm", "-p1.ai", "1", "-p2.ai", "1"]
    child = subprocess.Popen(args, cwd=working, creationflags=CREATE_SUSPENDED)

    ## share the launch info across processes
    launch_info = DebuggerLaunchInfo(child.pid, character_folder, DebugProcessState.SUSPENDED_WAIT)
    result = DebuggerTarget(child, launch_info)

    ## dispatch a thread to check when the subprocess closes + clean up automatically.
    threading.Thread(target=_wait_mugen, args=(result, character_folder)).start()

    ## dispatch a thread to handle debugging events from the target process
    threading.Thread(target=_debug_mugen, args=(launch_info, events_queue, results_queue)).start()

    ## dispatch a thread to read events processed by debugger and push them back to the debugger
    threading.Thread(target=_debug_handler, args=(launch_info, events_queue, results_queue)).start()

    print(f"Launched MUGEN suspended process. Type `continue` to continue.")

    return result

def cont(target: DebuggerTarget):
    if target.subprocess != None and target.launch_info.state == DebugProcessState.SUSPENDED_PROCEED:
        # resume the process, 
        psutil.Process(target.subprocess.pid).resume()
        target.launch_info.state = DebugProcessState.RUNNING
    elif target.subprocess != None and target.launch_info.state == DebugProcessState.PAUSED:
        results_queue.put(DebugBreakResult(True))
        target.launch_info.state = DebugProcessState.RUNNING