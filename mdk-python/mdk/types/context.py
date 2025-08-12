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
    target: int

@dataclass
class StateController:
    type: str
    params: dict[str, Expression]
    triggers: list[Expression]

    def __init__(self):
        self.type = ""
        self.params = {}
        self.triggers = []

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

@dataclass
class StateDefinition:
    fn: Callable
    params: dict[str, Expression]
    controllers: list[StateController]
    locals: list[ParameterDefinition]

@dataclass
class TemplateDefinition:
    fn: Callable
    library: Optional[str]
    params: dict[str, TypeSpecifier]
    controllers: list[StateController]
    locals: list[ParameterDefinition]

@dataclass
class TriggerDefinition:
    fn: Callable
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

    def __init__(self):
        self.statedefs = {}
        self.templates = {}
        self.triggers = {}
        self.current_state = None
        self.current_template = None
        self.current_trigger = None
        self.trigger_stack = []
        self.globals = []
    
    @classmethod
    def instance(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = CompilerContext()
        return cls._instance
