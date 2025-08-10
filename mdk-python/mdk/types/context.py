from dataclasses import dataclass
from typing import Callable, Optional

from mdk.types.specifier import TypeSpecifier
from mdk.types.expressions import Expression

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
class CompilerContext:
    statedefs: dict[str, StateDefinition]
    templates: dict[str, TemplateDefinition]
    current_state: Optional[StateDefinition]
    current_template: Optional[TemplateDefinition]
    current_trigger: Optional[Expression]
    trigger_stack: list[Expression]
    globals: list[ParameterDefinition]

    def __init__(self):
        self.statedefs = {}
        self.templates = {}
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

## EXTREMELY NASTY HACK
def _overwrite_bool(self: Expression):
    ## unfortunately this can't use mdk.utils.shared.get_context since that causes circular imports.
    ## but it can access the context itself here.
    ## we only need to set this expression onto TriggerStack when it is used as a bool.
    ctx = CompilerContext.instance()
    ctx.current_trigger = self
    return True
Expression.__bool__ = _overwrite_bool