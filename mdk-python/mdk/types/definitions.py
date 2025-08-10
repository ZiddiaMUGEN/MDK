from dataclasses import dataclass
from typing import Optional, Callable

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