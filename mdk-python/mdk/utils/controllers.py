from typing import Callable, Optional
import copy

from mdk.types.context import StateController, IntExpression

from mdk.utils.shared import format_bool, get_context

# decorator which provides a wrapper around each controller.
# this adds some extra debugging info, and also simplifies adding triggers to controllers and handling controller insertion into the active statedef.
def controller(fn: Callable) -> Callable:
    def wrapper(*args, ignorehitpause: Optional[bool] = None, persistent: Optional[int] = None, **kwargs):
        return make_controller(fn, *args, ignorehitpause = ignorehitpause, persistent = persistent, **kwargs)
    return wrapper
    
def make_controller(fn, *args, ignorehitpause: Optional[bool] = None, persistent: Optional[int] = None, **kwargs) -> StateController:
    ctrl: StateController = fn(*args, **kwargs)
    ctrl.type = fn.__name__
    if ignorehitpause != None: ctrl.params["ignorehitpause"] = format_bool(ignorehitpause)
    if persistent != None: ctrl.params["persistent"] = IntExpression(persistent)

    ctx = get_context()
    if ctx.current_state == None and ctx.current_template == None:
        raise Exception("Attempted to call a state controller outside of a statedef function.")
    
    ctrl.triggers = copy.deepcopy(ctx.trigger_stack)
    ctx.current_trigger = None
    
    if ctx.current_state != None:
        ctx.current_state.controllers.append(ctrl)
    elif ctx.current_template != None:
        ctx.current_template.controllers.append(ctrl)
    return ctrl