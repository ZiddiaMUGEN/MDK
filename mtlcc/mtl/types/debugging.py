from dataclasses import dataclass
import ctypes
from ctypes import c_int, c_short
import subprocess

from mtl.types.shared import Location
from mtl.types.translation import *

class DebuggerCommand(Enum):
    EXIT = -1
    NONE = 0
    HELP = 1
    LAUNCH = 2
    LOAD = 3
    CONTINUE = 4

class DebugProcessState(Enum):
    EXIT = -1 # indicates the process is exited or wants to exit.
    RUNNING = 0 # process is running and has not hit a breakpoint.
    SUSPENDED_WAIT = 1 # process is suspended, waiting for debugger to attach.
    SUSPENDED_PROCEED = 2 # process is suspended, debugger is attached.
    PAUSED = 3 # process is paused by a breakpoint.

@dataclass
class DebuggerRequest:
    command_type: DebuggerCommand
    params: list[str]

@dataclass
class DebuggerLaunchInfo:
    process_id: int
    character_folder: Optional[str]
    state: DebugProcessState

@dataclass
class DebuggerTarget:
    subprocess: subprocess.Popen
    launch_info: DebuggerLaunchInfo

@dataclass
class DebugTypeInfo:
    name: str
    category: TypeCategory
    members: list[Union[str, TypeDefinition, 'DebugTypeInfo']]
    member_names: list[str]
    location: Location

@dataclass
class DebugTriggerInfo:
    name: str
    category: TriggerCategory
    returns: Union[TypeDefinition, DebugTypeInfo]
    parameter_types: list[Union[TypeDefinition, DebugTypeInfo]]
    parameter_names: list[str]
    expression: Optional[TriggerTree]
    location: Location

@dataclass
class DebugTemplateInfo:
    name: str
    category: TemplateCategory
    parameter_types: list[Union[list[TypeSpecifier], list[DebugTypeInfo]]]
    parameter_names: list[str]
    local_types: list[Union[TypeDefinition, DebugTypeInfo]]
    local_names: list[str]
    location: Location

@dataclass
class DebugParameterInfo:
    name: str
    type: Union[TypeDefinition, DebugTypeInfo]
    scope: StateDefinitionScope
    allocations: list[tuple[int, int]]

@dataclass
class DebugStateInfo:
    name: str
    id: int
    scope: StateDefinitionScope
    location: Location
    locals: list[DebugParameterInfo]
    states: list[Location]

@dataclass
class DebuggingContext:
    strings: list[str]
    types: list[DebugTypeInfo]
    triggers: list[DebugTriggerInfo]
    templates: list[DebugTemplateInfo]
    globals: list[DebugParameterInfo]
    states: list[DebugStateInfo]

    def __init__(self):
        self.strings = []
        self.types = []
        self.triggers = []
        self.templates = []
        self.globals = []
        self.states = []

class EXCEPTION_RECORD(ctypes.Structure):
    _fields_ = [
        ("ExceptionCode", c_int),
        ("ExceptionFlags", c_int),
        ("ExceptionRecord", c_int),
        ("ExceptionAddress", c_int),
        ("NumberParameters", c_int),
        ("ExceptionInformation", c_int)
    ]

class EXCEPTION_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("ExceptionRecord", EXCEPTION_RECORD),
        ("dwFirstChance", c_int)
    ]

class CREATE_THREAD_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("hThread", c_int),
        ("lpThreadLocalBase", c_int),
        ("lpStartAddress", c_int),
    ]

class CREATE_PROCESS_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("hFile", c_int),
        ("hProcess", c_int),
        ("hThread", c_int),
        ("lpBaseOfImage", c_int),
        ("dwDebugInfoFileOffset", c_int),
        ("nDebugInfoSize", c_int),
        ("lpThreadLocalBase", c_int),
        ("lpStartAddress", c_int),
        ("lpImageName", c_int),
        ("fUnicode", c_short),
    ]

class EXIT_THREAD_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("dwExitCode", c_int)
    ]

class EXIT_PROCESS_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("dwExitCode", c_int)
    ]

class LOAD_DLL_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("hFile", c_int),
        ("lpBaseOfDll", c_int),
        ("dwDebugInfoFileOffset", c_int),
        ("nDebugInfoSize", c_int),
        ("lpImageName", c_int),
        ("fUnicode", c_short),
    ]

class UNLOAD_DLL_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("lpBaseOfDll", c_int)
    ]

class OUTPUT_DEBUG_STRING_INFO(ctypes.Structure):
    _fields_ = [
        ("lpDebugStringData", c_int),
        ("fUnicode", c_short),
        ("nDebugStringLength", c_short)
    ]

class RIP_INFO(ctypes.Structure):
    _fields_ = [
        ("dwError", c_int),
        ("dwType", c_int),
    ]

class DEBUG_INFO(ctypes.Union):
    _fields_ = [
        ("Exception", EXCEPTION_DEBUG_INFO),
        ("CreateThread", CREATE_THREAD_DEBUG_INFO),
        ("CreateProcessInfo", CREATE_PROCESS_DEBUG_INFO),
        ("ExitThread", EXIT_THREAD_DEBUG_INFO),
        ("ExitProcess", EXIT_PROCESS_DEBUG_INFO),
        ("LoadDll", LOAD_DLL_DEBUG_INFO),
        ("UnloadDll", UNLOAD_DLL_DEBUG_INFO),
        ("DebugString", OUTPUT_DEBUG_STRING_INFO),
        ("RipInfo", RIP_INFO)
    ]

class DEBUG_EVENT(ctypes.Structure):
    _fields_ = [
        ("dwDebugEventCode", c_int),
        ("dwProcessId", c_int),
        ("dwThreadId", c_int),
        ("u", DEBUG_INFO)
    ]