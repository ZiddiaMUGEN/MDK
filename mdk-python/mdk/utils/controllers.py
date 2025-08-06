from typing import Callable, Optional
import copy

from mdk.types.context import StateController, IntExpression

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
    