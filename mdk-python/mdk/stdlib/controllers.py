from typing import Union, Callable, Optional
from functools import partial

from mdk.utils.controllers import controller
from mdk.types.context import StateController, Expression, StateNoType, IntType, BoolType

@controller
def ChangeState(value: Union[Expression, str, Callable, int], ctrl: Optional[Expression] = None, anim: Optional[Expression] = None) -> StateController:
    result = StateController()

    if isinstance(value, Expression): assert(value.type == StateNoType or value.type == IntType)
    if ctrl != None: assert(ctrl.type == BoolType)
    if anim != None: assert(anim.type == IntType)

    if isinstance(value, partial):
        result.params["value"] = Expression(value.keywords["value"], StateNoType)
    elif isinstance(value, Callable):
        result.params["value"] = Expression(value.__name__, StateNoType)
    elif isinstance(value, str):
        result.params["value"] = Expression(value, StateNoType)
    elif isinstance(value, int):
        result.params["value"] = Expression(str(value), StateNoType)
    else:
        result.params["value"] = value

    if ctrl != None:
        result.params["ctrl"] = ctrl
    
    if anim != None:
        result.params["anim"] = anim

    return result