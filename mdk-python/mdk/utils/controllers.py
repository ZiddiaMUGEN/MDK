from typing import Callable, Optional, Union
import copy

from mdk.types.context import StateController, CompilerContext
from mdk.types.expressions import Expression, TupleExpression
from mdk.types.builtins import IntType, StringType, FloatType, BoolType
from mdk.types.defined import TupleType
from mdk.types.specifier import TypeSpecifier

from mdk.utils.shared import format_bool, format_tuple

# decorator which provides a wrapper around each controller.
# this adds some extra debugging info, and also simplifies adding triggers to controllers and handling controller insertion into the active statedef.
def controller(**typeinfo) -> Callable:
    def wrapper(fn: Callable) -> Callable:
        def decorated(*args, ignorehitpause: Optional[bool] = None, persistent: Optional[int] = None, **kwargs):
            return make_controller(fn, *args, typeinfo = typeinfo, ignorehitpause = ignorehitpause, persistent = persistent, **kwargs)
        return decorated
    return wrapper
    
def make_controller(fn, *args, typeinfo: dict[str, list[Optional[TypeSpecifier]]], ignorehitpause: Optional[bool] = None, persistent: Optional[int] = None, **kwargs) -> StateController:
    new_kwargs: dict[str, Union[Expression, TupleExpression]] = copy.deepcopy(kwargs)
    for name in typeinfo:
        valid_types = typeinfo[name]
        valid_typenames = [type.name for type in valid_types if type != None]
        ## 1. ensure required params are included
        if None not in valid_types and name not in kwargs:
            raise Exception(f"Controller {fn.__name__} has a required parameter {name} which was not provided.")
        ## 2. ensure types are correct
        if name in kwargs:
            input_expression = kwargs[name]
            if isinstance(input_expression, Expression):
                input_type = input_expression.type
                if input_type not in valid_types:
                    raise Exception(f"Parameter {name} on controller {fn.__name__} expects an expression with a type from ({', '.join(valid_typenames)}), but got {input_type.name} instead.")
                new_kwargs[name] = input_expression
            elif type(input_expression) == int:
                if IntType not in valid_types:
                    raise Exception(f"Parameter {name} on controller {fn.__name__} expects an expression with a type from ({', '.join(valid_typenames)}), but got a builtin `int` instead.")
                new_kwargs[name] = Expression(str(input_expression), IntType)
            elif type(input_expression) == str:
                if StringType not in valid_types:
                    raise Exception(f"Parameter {name} on controller {fn.__name__} expects an expression with a type from ({', '.join(valid_typenames)}), but got a builtin `str` instead.")
                new_kwargs[name] = Expression(str(input_expression), StringType)
            elif type(input_expression) == float:
                if FloatType not in valid_types:
                    raise Exception(f"Parameter {name} on controller {fn.__name__} expects an expression with a type from ({', '.join(valid_typenames)}), but got a builtin `float` instead.")
                new_kwargs[name] = Expression(str(input_expression), FloatType)
            elif type(input_expression) == bool:
                if BoolType not in valid_types:
                    raise Exception(f"Parameter {name} on controller {fn.__name__} expects an expression with a type from ({', '.join(valid_typenames)}), but got a builtin `bool` instead.")
                new_kwargs[name] = format_bool(input_expression)
            elif type(input_expression) == tuple:
                ## for a tuple, we expect TupleExpression in the valid types. there should be exactly 1 valid type.
                valid_no_none = [t for t in valid_types if t != None]
                if len(valid_no_none) != 1 or not isinstance(valid_no_none[0], TupleType):
                    raise Exception(f"Controller {fn.__name__} has a parameter {name} which expects an expression with a type from ({', '.join(valid_typenames)}), but parameter required {type(valid_no_none[0])} - bug the developers.")
                target_type = valid_no_none[0]
                ## although we provide typings for the tuple, we don't actually check them here.
                ## (mdk-python's current API does not encode optional/repeated tuple members, so the type check is incorrect anyway)
                ## this is fine since MTL will catch any mistakes during translation, as MTL itself supports these features.
                new_kwargs[name] = format_tuple(input_expression)
            else:
                raise Exception(f"Couldn't determine input type for parameter {name} on controller {fn.__name__}; input type was {type(input_expression)}.")

    ctrl: StateController = fn(*args, **new_kwargs)
    ctrl.type = fn.__name__
    if ignorehitpause != None: ctrl.params["ignorehitpause"] = format_bool(ignorehitpause)
    if persistent != None: ctrl.params["persistent"] = Expression(str(persistent), IntType)

    ctx = CompilerContext.instance()
    if ctx.current_state == None and ctx.current_template == None:
        raise Exception("Attempted to call a state controller outside of a statedef function.")
    
    ctrl.triggers = copy.deepcopy(ctx.trigger_stack)
    ctx.current_trigger = None
    
    if ctx.current_state != None:
        ctx.current_state.controllers.append(ctrl)
    elif ctx.current_template != None:
        ctx.current_template.controllers.append(ctrl)
    return ctrl