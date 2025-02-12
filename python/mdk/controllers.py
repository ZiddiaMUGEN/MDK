# contains a definition for each built-in state controller.
# this provides an interface to CNS controllers with properly-typed parameters.
from typing import Union, Optional
from collections.abc import Callable

from mdk.utils import debug, format_bool
from mdk.triggers import Trigger
from mdk import state

TriggerInt = Union[Trigger, int]
TriggerFloat = Union[Trigger, float]
TriggerBool = Union[Trigger, bool]

# decorator which provides a wrapper around each controller.
# this adds some extra debugging info, and also simplifies adding triggers to controllers and handling controller insertion into the active statedef.
def controller(fn: Callable) -> Callable:
    def wrapper(*args, ignorehitpause: Optional[bool] = None, persistent: Optional[int] = None, **kwargs):
        debug(f"Executing controller {fn.__name__} with args: {args}, {kwargs}")
        ctrl: state.Controller = fn(*args, **kwargs)
        ctrl.type = fn.__name__
        if ignorehitpause != None: ctrl.params["ignorehitpause"] = format_bool(ignorehitpause)
        if persistent != None: ctrl.params["persistent"] = int(persistent)
        if state.CURRENT_EXPRESSION != None: ctrl.add_trigger(1, state.CURRENT_EXPRESSION)
        state.CURRENT_EXPRESSION = None
        state.CURRENT_STATEDEF.controllers.append(ctrl)
    return wrapper

@controller
def ChangeState(value: Union[TriggerInt, str, Callable], ctrl: Optional[TriggerBool] = None, anim: Optional[TriggerInt] = None) -> state.Controller:
    result = state.Controller()

    if type(value) == Callable:
        result.params["value"] = value.__name__
    else:
        result.params["value"] = value

    if ctrl != None:
        result.params["ctrl"] = ctrl
    
    if anim != None:
        result.params["anim"] = anim

    return result

@controller
def ChangeAnim(value: TriggerInt, elem: Optional[TriggerInt] = None) -> state.Controller:
    result = state.Controller()

    result.params["value"] = value
    if elem != None:
        result.params["elem"] = elem

    return result

@controller
def VelSet(x: Optional[TriggerFloat] = None, y: Optional[TriggerFloat] = None) -> state.Controller:
    result = state.Controller()

    if x != None:
        result.params["x"] = x
    if y != None:
        result.params["y"] = y

    return result