from dataclasses import dataclass

from mtl.types.shared import Location
from mtl.types.translation import *

class DebuggerCommand(Enum):
    EXIT = -1
    NONE = 0
    HELP = 1
    LAUNCH = 2
    LOAD = 3

@dataclass
class DebuggerRequest:
    command_type: DebuggerCommand
    params: list[str]

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
