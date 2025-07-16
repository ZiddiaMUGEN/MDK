from collections.abc import Callable
from typing import Dict, List, Union, Optional

class Statedef:
    def __init__(self, name: str):
        self.name: str = name
        self.controllers: List[Controller] = []
        self.params: Dict[str, str] = {}
        self.stateno: Optional[int] = None

class Controller:
    def __init__(self):
        self.comment: Optional[str] = None
        self.type: str = ""
        self.params: Dict[str, Union[str, int, float]] = {}
        # indexed first by group, then as an array. e.g. self.triggers["1"] may contain multiple triggers for this group.
        self.triggers: Dict[List[str]] = {}
    def add_trigger(self, group: int, trigger: str):
        if group not in self.triggers: self.triggers[group] = []
        self.triggers[group].append(trigger)

class StatedefImpl:
    def __init__(self, fn: Callable):
        self.fn: Callable = fn
        self.params: Dict[str, str] = {}
        self.stateno: Optional[int] = None

## stores a reference from statedef name to the backing function.
ALL_STATEDEF_IMPLS: Dict[str, StatedefImpl] = {}

## stores all current Statedefs which have been built.
ALL_STATEDEF_CNS: Dict[str, Statedef] = {}

## stores any controllers which apply at the global scope. tMUGEN is responsible for converting these into one-off executions in -2.
GLOBAL_CONTROLLERS: List[Controller] = []

## stores the Statedef which is currently being built.
CURRENT_STATEDEF: Statedef = None

## stores the current trigger expression representation, and the stack of all applied trigger expressions.
CURRENT_EXPRESSION: Optional[str] = None
EXPRESSION_STACK: List[str] = []