from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, TYPE_CHECKING
from enum import Enum

from mdk.types.specifier import TypeSpecifier

## an ugly hack, necessary due to circular import.
if TYPE_CHECKING:
    from mdk.types.expressions import Expression

class StateScopeType(Enum):
    SHARED = 0
    PLAYER = 1
    HELPER = 2
    TARGET = 3

@dataclass
class StateScope:
    scope: StateScopeType
    target: Optional[int] = None
    def __str__(self) -> str:
        if self.scope == StateScopeType.SHARED:
            return "shared"
        elif self.scope == StateScopeType.PLAYER:
            return "player"
        elif self.scope == StateScopeType.TARGET:
            return "target"
        elif self.scope == StateScopeType.HELPER:
            if self.target == None: return "helper"
            return f"helper({self.target})"
        return "<?>"
    
SCOPE_TARGET = StateScope(StateScopeType.TARGET)
SCOPE_PLAYER = StateScope(StateScopeType.PLAYER)
SCOPE_HELPER: Callable[[Optional[int]], StateScope] = lambda id: StateScope(StateScopeType.HELPER, id)

@dataclass
class StateController:
    type: str
    params: dict[str, Expression]
    triggers: list[Expression]
    location: tuple[str, int]

    def __init__(self):
        self.type = ""
        self.params = {}
        self.triggers = []
        self.location = ("<?>", 0)

    def __repr__(self):
        result = "[State ]"
        result += f"\ntype = {self.type}"
        for trigger in self.triggers:
            result += f"\ntrigger1 = {trigger}"
        for param in self.params:
            result += f"\n{param} = {self.params[param]}"
        return result
    
@dataclass
class ParameterDefinition:
    type: TypeSpecifier
    name: str
    ## this is only supported for globals.
    ## by default globals use SHARED scope, but we should be able to specify.
    scope: Optional[StateScope] = None

@dataclass
class StateDefinition:
    fn: Callable[[], None]
    params: dict[str, Expression]
    controllers: list[StateController]
    locals: list[ParameterDefinition]
    scope: Optional[StateScope]

@dataclass
class TemplateDefinition:
    fn: Callable[..., None]
    library: Optional[str]
    params: dict[str, TypeSpecifier]
    controllers: list[StateController]
    locals: list[ParameterDefinition]

@dataclass
class TriggerDefinition:
    fn: Callable[..., Expression]
    library: Optional[str]
    result: TypeSpecifier
    params: dict[str, TypeSpecifier]
    exprn: Optional[Expression] = None

@dataclass
class CompilerContext:
    statedefs: dict[str, StateDefinition]
    templates: dict[str, TemplateDefinition]
    triggers: dict[str, TriggerDefinition]
    current_state: Optional[StateDefinition]
    current_template: Optional[TemplateDefinition]
    current_trigger: Optional[Expression]
    trigger_stack: list[Expression]
    globals: list[ParameterDefinition]
    default_state: tuple[Expression | None, Expression | None]

    def __init__(self):
        self.statedefs = {}
        self.templates = {}
        self.triggers = {}
        self.current_state = None
        self.current_template = None
        self.current_trigger = None
        self.trigger_stack = []
        self.globals = []
        self.default_state = (None, None)
    
    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = CompilerContext()
        return cls._instance
