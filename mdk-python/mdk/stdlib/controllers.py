from typing import Union, Callable, Optional
from functools import partial

from mdk.utils.controllers import controller
from mdk.types.context import StateController, Expression, IntExpression, BoolExpression

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