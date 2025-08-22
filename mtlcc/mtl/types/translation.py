from dataclasses import dataclass, field
from typing import Optional, Union, Callable, Any
from enum import Enum

from mtl.types.ini import StateControllerProperty
from mtl.types.shared import Location
from mtl.types.trigger import TriggerTree

class TypeCategory(Enum):
    INVALID = -1
    ALIAS = 0
    UNION = 1
    ENUM = 2
    FLAG = 3
    STRUCTURE = 4
    BUILTIN_STRUCTURE = 96 # special builtin type for things such as Vel/Pos where the struct access is preserved in the output.
    STRING_FLAG = 97 # special builtin type for things such as hitdefattr where the flag identifier is preserved in the output.
    STRING_ENUM = 98 # special builtin type for things such as movetype, statetype, etc where the enum identifier is preserved in the output.
    BUILTIN = 99 # special builtin types (int, float, etc) which need to exist for type-checking.
    BUILTIN_DENY = 100 # builtin types which you cannot allocate.

@dataclass
class TypeDefinition:
    name: str
    category: TypeCategory
    ## size is expressed in bits (to support 1-bit bool)
    size: int
    # valid values for 'members' depends on the category.
    # - for ALIAS, there must be exactly 1 member, matching another type name.
    # - for UNION, there can be as many members as needed, with matching sizes.
    # - for ENUM, the members define the valid values the enumeration can take; enumeration IDs are assigned in order.
    # - for FLAG, the members define the valid flag values which can be set; a maximum of 32 members can be added.
    # - for STRUCTURE, the members are a mapping from a name to a type.
    members: list[str]
    location: Location

@dataclass
class TypeParameter:
    name: str
    type: TypeDefinition
    default: Optional[TriggerTree] = None
    location: Location = field(default_factory=lambda: Location("", 0))
    ## this needs to be a list of allocations to support structure types.
    allocations: list[tuple[int, int]] = field(default_factory=lambda: [])
    ## scopes need to be baked in.
    scope: 'StateDefinitionScope' = field(default_factory=lambda: StateDefinitionScope(StateScopeType.SHARED, None))
    ## global forwards use this to specify sysvar-level storage.
    is_system: bool = False

@dataclass
class ForwardParameter:
    name: str
    type: str
    is_system: bool = False
    scope: 'StateDefinitionScope' = field(default_factory=lambda: StateDefinitionScope(StateScopeType.SHARED, None))

class TriggerCategory(Enum):
    SIMPLE = 0
    CONST = 1
    OPERATOR = 2
    BUILTIN = 99

@dataclass
class Expression:
    type: TypeDefinition
    value: str

@dataclass
class VariableExpression(Expression):
    allocation: tuple[int, int]
    is_float: bool
    is_system: bool

@dataclass
class RescopeExpression(Expression):
    target: 'StateDefinitionScope'

@dataclass
class TriggerDefinition:
    name: str
    type: TypeDefinition
    const: Union[Callable[[list[Expression], Any], Expression], None]
    params: list[TypeParameter]
    exprn: Optional[TriggerTree]
    location: Location
    _lower: str
    category: TriggerCategory = TriggerCategory.SIMPLE

class TemplateCategory(Enum):
    DEFINED = 0
    BUILTIN = 1

@dataclass
class TriggerGroup:
    triggers: list[TriggerTree]

@dataclass
class StateController:
    name: str
    triggers: dict[int, TriggerGroup]
    properties: list[StateControllerProperty]
    location: Location

@dataclass
class TypeSpecifier:
    type: TypeDefinition
    required: bool = True
    repeat: bool = False

@dataclass
class TemplateParameter:
    name: str
    type: list[TypeSpecifier]
    required: bool = True

@dataclass
class TemplateDefinition:
    name: str
    params: list[TemplateParameter]
    locals: list[TypeParameter]
    states: list[StateController]
    location: Location
    category: TemplateCategory = TemplateCategory.DEFINED

@dataclass
class StateDefinitionParameters:
    type: Optional[str] = None
    movetype: Optional[str] = None
    physics: Optional[str] = None
    anim: Optional[int] = None
    velset: Optional[tuple[float, float]] = None
    ctrl: Optional[bool] = None
    poweradd: Optional[int] = None
    juggle: Optional[int] = None
    facep2: Optional[bool] = None
    hitdefpersist: Optional[bool] = None
    movehitpersist: Optional[bool] = None
    hitcountpersist: Optional[bool] = None
    sprpriority: Optional[int] = None
    id: Optional[int] = None
    is_common: bool = False

class StateScopeType(Enum):
    SHARED = 0
    PLAYER = 1
    HELPER = 2
    TARGET = 3

@dataclass
class StateDefinitionScope:
    type: StateScopeType
    target: Optional[int]

    def __eq__(self, other):
        if not isinstance(other, StateDefinitionScope):
            return NotImplemented
        return self.type == other.type and self.target == other.target
    
    def __hash__(self):
        return hash((self.type, self.target))

@dataclass
class StateDefinition:
    name: str
    parameters: StateDefinitionParameters
    locals: list[TypeParameter]
    states: list[StateController]
    scope: StateDefinitionScope
    location: Location

@dataclass
class AllocationTable:
    data: dict[int, int]
    max_size: int