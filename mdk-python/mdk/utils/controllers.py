from typing import Union, Callable, Optional
from functools import partial
import copy

from mdk.types.builtins import Expression, IntExpression, BoolExpression
from mdk.types.context import StateController

from mdk.utils.shared import format_bool, get_context

# decorator which provides a wrapper around each controller.
# this adds some extra debugging info, and also simplifies adding triggers to controllers and handling controller insertion into the active statedef.
def controller(fn: Callable) -> Callable:
    def wrapper(*args, ignorehitpause: Optional[bool] = None, persistent: Optional[int] = None, append: bool = True, **kwargs):
        ctrl: StateController = fn(*args, **kwargs)
        ctrl.type = fn.__name__
        if ignorehitpause != None: ctrl.params["ignorehitpause"] = format_bool(ignorehitpause)
        if persistent != None: ctrl.params["persistent"] = IntExpression(persistent)

        ctx = get_context()
        if ctx.current_state == None:
            raise Exception("Attempted to call a state controller outside of a statedef function.")
        ctrl.triggers = copy.deepcopy(ctx.trigger_stack)
        ctx.current_trigger = None
        ctx.current_state.controllers.append(ctrl)
        return ctrl
    return wrapper

@controller
def ChangeState(value: Union[IntExpression, str, Callable], ctrl: Optional[BoolExpression] = None, anim: Optional[IntExpression] = None) -> StateController:
    result = StateController()

    if isinstance(value, partial):
        result.params["value"] = Expression(value.keywords["value"])
    elif isinstance(value, Callable):
        result.params["value"] = Expression(value.__name__)
    elif isinstance(value, str):
        result.params["value"] = Expression(value)
    else:
        result.params["value"] = value

    if ctrl != None:
        result.params["ctrl"] = ctrl
    
    if anim != None:
        result.params["anim"] = anim

    return result
    