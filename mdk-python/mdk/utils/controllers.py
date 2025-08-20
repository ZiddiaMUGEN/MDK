from typing import Callable, Optional, Union
import copy
import functools
import traceback

from mdk.types.context import StateController, CompilerContext
from mdk.types.expressions import Expression, TupleExpression
from mdk.types.builtins import IntType, StateNoType, AnyType
from mdk.types.defined import TupleType
from mdk.types.specifier import TypeSpecifier

from mdk.utils.shared import format_bool, format_tuple, convert
from mdk.utils.expressions import check_any_assignable

# decorator which provides a wrapper around each controller.
# this adds some extra debugging info, and also simplifies adding triggers to controllers and handling controller insertion into the active statedef.
def controller(**typeinfo) -> Callable[[Callable[..., StateController]], Callable[..., StateController]]:
    def wrapper(fn: Callable[..., StateController]) -> Callable[..., StateController]:
        def decorated(*args, ignorehitpause: Optional[bool] = None, persistent: Optional[int] = None, **kwargs) -> StateController:
            return make_controller(fn, *args, typeinfo = typeinfo, ignorehitpause = ignorehitpause, persistent = persistent, **kwargs)
        return decorated
    return wrapper
    
def make_controller(fn, *args, typeinfo: dict[str, list[Optional[TypeSpecifier]]], ignorehitpause: Optional[bool] = None, persistent: Optional[int] = None, **kwargs) -> StateController:
    new_kwargs: dict[str, Union[Expression, TupleExpression]] = {}
    for name in typeinfo:
        valid_types = typeinfo[name]
        valid_no_none = [t for t in valid_types if t != None]
        valid_typenames = [type.name for type in valid_types if type != None]
        ## 1. ensure required params are included
        if None not in valid_types and name not in kwargs:
            raise Exception(f"Controller {fn.__name__} has a required parameter {name} which was not provided.")
        ## 2. ensure types are correct
        if name in kwargs:
            input_expression = kwargs[name]
            if type(input_expression) in [int, str, float, bool]:
                input_expression = convert(input_expression)
            if isinstance(input_expression, Expression):
                input_type = input_expression.type
                if check_any_assignable(input_type, valid_no_none) == None:
                    raise Exception(f"Parameter {name} on controller {fn.__name__} expects an expression with a type from ({', '.join(valid_typenames)}), but got {input_type.name} instead.")
                new_kwargs[name] = input_expression
            elif type(input_expression) == tuple:
                ## for a tuple, we expect TupleExpression in the valid types. there should be exactly 1 valid type.
                if len(valid_no_none) != 1 or (not isinstance(valid_no_none[0], TupleType) and valid_no_none[0] != AnyType):
                    raise Exception(f"Controller {fn.__name__} has a parameter {name} which expects an expression with a type from ({', '.join(valid_typenames)}), but parameter required {type(valid_no_none[0])} - bug the developers.")
                target_type = valid_no_none[0]
                ## although we provide typings for the tuple, we don't actually check them here.
                ## (mdk-python's current API does not encode optional/repeated tuple members, so the type check is incorrect anyway)
                ## this is fine since MTL will catch any mistakes during translation, as MTL itself supports these features.
                new_kwargs[name] = format_tuple(input_expression)
            elif type(input_expression) in [functools.partial, Callable] and StateNoType in valid_types:
                ## you're allowed to use function pointers directly as stateno types.
                new_kwargs[name] = input_expression
            elif input_expression != None:
                ## required parameters were already checked, so if None was passed explicitly it's completely fine. we just skip that parameter.
                raise Exception(f"Couldn't determine input type for parameter {name} on controller {fn.__name__}; input type was {type(input_expression)}.")

    ctrl: StateController = fn(*args, **new_kwargs)
    ctrl.type = fn.__name__

    ctx = CompilerContext.instance()
    if ctx.default_state[0] != None: ctrl.params["ignorehitpause"] = ctx.default_state[0]
    if ctx.default_state[1] != None: ctrl.params["persistent"] = ctx.default_state[1]

    if ignorehitpause != None: ctrl.params["ignorehitpause"] = format_bool(ignorehitpause)
    if persistent != None: ctrl.params["persistent"] = Expression(str(persistent), IntType)
    
    if ctx.current_state == None and ctx.current_template == None:
        raise Exception("Attempted to call a state controller outside of a statedef function.")
    
    ctrl.triggers = copy.deepcopy(ctx.trigger_stack)
    ctx.current_trigger = None

    ## i believe this should always be right, since it flows from <callsite> -> decorated -> make_controller
    callsite = traceback.extract_stack()[-3]
    ctrl.location = (callsite.filename, callsite.lineno if callsite.lineno != None else 0)
    
    if ctx.current_state != None:
        ctx.current_state.controllers.append(ctrl)
    elif ctx.current_template != None:
        ctx.current_template.controllers.append(ctrl)
    return ctrl