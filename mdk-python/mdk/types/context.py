from dataclasses import dataclass
from typing import Callable, Optional

from mdk.types.builtins import Expression

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
class StateDefinition:
    fn: Callable
    params: dict[str, Expression]
    controllers: list[StateController]

@dataclass
class CompilerContext:
    statedefs: dict[str, StateDefinition]
    current_state: Optional[StateDefinition]
    current_trigger: Optional[Expression]
    trigger_stack: list[Expression]

    def __init__(self):
        self.statedefs = {}
        self.current_state = None
        self.current_trigger = None
        self.trigger_stack = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CompilerContext, cls).__new__(cls)
        return cls.instance