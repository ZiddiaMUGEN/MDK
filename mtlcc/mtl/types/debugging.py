from dataclasses import dataclass
import ctypes
from ctypes import c_int, c_short, wintypes
import subprocess

from mtl.types.shared import Location
from mtl.types.translation import *

CREATE_SUSPENDED = 4
INFINITE = 0xffffffff
DBG_CONTINUE = 0x00010002
PROCESS_ALL_ACCESS = 0x001FFFFF
THREAD_GET_SET_CONTEXT = 0x5A

EXCEPTION_DEBUG_EVENT = 1
CREATE_PROCESS_DEBUG_EVENT = 3

STATUS_WX86_SINGLE_STEP = 0x4000001E
STATUS_WX86_BREAKPOINT = 0x4000001F
STATUS_BREAKPOINT = 0x80000003
STATUS_SINGLE_STEP = 0x80000004

RESUME_FLAG = 0x00010000

CONTEXT_AMD64 = 0x00100000
CONTEXT_CONTROL = (CONTEXT_AMD64 | 0x00000001)
CONTEXT_INTEGER = (CONTEXT_AMD64 | 0x00000002)
CONTEXT_DEBUG_REGISTERS = (CONTEXT_AMD64 | 0x00000010)

class DebuggerCommand(Enum):
    EXIT = -1
    NONE = 0
    HELP = 1
    LAUNCH = 2
    LOAD = 3
    CONTINUE = 4
    INFO = 5
    BREAK = 6
    STEP = 7
    STOP = 8

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
    thread_id: int
    character_folder: Optional[str]
    state: DebugProcessState
    current_bp: Optional[tuple[int, int]]

@dataclass
class DebuggerTarget:
    subprocess: subprocess.Popen
    launch_info: DebuggerLaunchInfo

@dataclass
class DebugBreakEvent:
    address: int
    step: Optional[tuple[int, int]]

@dataclass
class DebugBreakResult:
    step: bool = True

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
        ("ExceptionCode", wintypes.DWORD),
        ("ExceptionFlags", wintypes.DWORD),
        ("ExceptionRecord", ctypes.POINTER(wintypes.DWORD)),
        ("ExceptionAddress", wintypes.LPVOID),
        ("NumberParameters", wintypes.DWORD),
        ("ExceptionInformation", wintypes.LPVOID * 15)
    ]

class EXCEPTION_DEBUG_INFO(ctypes.Structure):
    _fields_ = [
        ("ExceptionRecord", EXCEPTION_RECORD),
        ("dwFirstChance", wintypes.DWORD)
    ]

class DEBUG_INFO(ctypes.Union):
    _fields_ = [
        ("Exception", EXCEPTION_DEBUG_INFO)
    ]

class DEBUG_EVENT(ctypes.Structure):
    _fields_ = [
        ("dwDebugEventCode", wintypes.DWORD),
        ("dwProcessId", wintypes.DWORD),
        ("dwThreadId", wintypes.DWORD),
        ("u", DEBUG_INFO)
    ]

class FLOATING_SAVE_AREA(ctypes.Structure):
    _fields_ = [
        ("ControlWord", wintypes.DWORD),
        ("StatusWord", wintypes.DWORD),
        ("TagWord", wintypes.DWORD),
        ("ErrorOffset", wintypes.DWORD),
        ("ErrorSelector", wintypes.DWORD),
        ("DataOffset", wintypes.DWORD),
        ("DataSelector", wintypes.DWORD),
        ("RegisterArea", wintypes.BYTE * 80),
        ("Cr0NpxState", wintypes.DWORD),
    ]

class CONTEXT(ctypes.Structure):
    _fields_ = [
        ("ContextFlags", wintypes.DWORD),
        ("Dr0", wintypes.DWORD),
        ("Dr1", wintypes.DWORD),
        ("Dr2", wintypes.DWORD),
        ("Dr3", wintypes.DWORD),
        ("Dr6", wintypes.DWORD),
        ("Dr7", wintypes.DWORD),
        ("FloatSave", FLOATING_SAVE_AREA),
        ("SegGs", wintypes.DWORD),
        ("SegFs", wintypes.DWORD),
        ("SegEs", wintypes.DWORD),
        ("SegDs", wintypes.DWORD),
        ("Edi", wintypes.DWORD),
        ("Esi", wintypes.DWORD),
        ("Ebx", wintypes.DWORD),
        ("Edx", wintypes.DWORD),
        ("Ecx", wintypes.DWORD),
        ("Eax", wintypes.DWORD),
        ("Ebp", wintypes.DWORD),
        ("Eip", wintypes.DWORD),
        ("SegCs", wintypes.DWORD),
        ("EFlags", wintypes.DWORD),
        ("Esp", wintypes.DWORD),
        ("SegSs", wintypes.DWORD),
        ("ExtendedRegisters", wintypes.BYTE * 512)
    ]