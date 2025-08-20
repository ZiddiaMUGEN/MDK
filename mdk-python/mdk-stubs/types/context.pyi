from dataclasses import dataclass
from enum import Enum
from mdk.types.expressions import Expression as Expression
from mdk.types.specifier import TypeSpecifier as TypeSpecifier
from typing import Callable, Optional

class StateScopeType(Enum):
    SHARED = 0
    PLAYER = 1
    HELPER = 2
    TARGET = 3

@dataclass
class StateScope:
    scope: StateScopeType
    target: Optional[int] = None

SCOPE_TARGET: StateScope
SCOPE_PLAYER: StateScope
SCOPE_HELPER: Callable[[Optional[int]], StateScope]

@dataclass
class StateController:
    type: str
    params: dict[str, Expression]
    triggers: list[Expression]
    location: tuple[str, int]
    def __init__(self) -> None: ...

@dataclass
class ParameterDefinition:
    type: TypeSpecifier
    name: str
    scope: StateScope | None = None

@dataclass
class StateDefinition:
    fn: Callable[[], None]
    params: dict[str, Expression]
    controllers: list[StateController]
    locals: list[ParameterDefinition]

@dataclass
class TemplateDefinition:
    fn: Callable[..., None]
    library: str | None
    params: dict[str, TypeSpecifier]
    controllers: list[StateController]
    locals: list[ParameterDefinition]

@dataclass
class TriggerDefinition:
    fn: Callable[..., Expression]
    library: str | None
    result: TypeSpecifier
    params: dict[str, TypeSpecifier]
    exprn: Expression | None = ...

@dataclass
class CompilerContext:
    statedefs: dict[str, StateDefinition]
    templates: dict[str, TemplateDefinition]
    triggers: dict[str, TriggerDefinition]
    typedefs: dict[str, TypeSpecifier]
    current_state: StateDefinition | None
    current_template: TemplateDefinition | None
    current_trigger: Expression | None
    trigger_stack: list[Expression]
    globals: list[ParameterDefinition]
    default_state: tuple[Expression | None, Expression | None]
    format_params: list[Expression]
    def __init__(self) -> None: ...
    @classmethod
    def instance(cls) -> CompilerContext: ...
