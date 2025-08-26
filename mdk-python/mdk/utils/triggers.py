from mdk.types.context import CompilerContext
from mdk.types.expressions import Expression
from mdk.types.variables import VariableExpression
from mdk.types.builtins import BoolType, IntType, ShortType, ByteType
from mdk.types.defined import StateNoType, EnumType, FlagType

from mdk.stdlib.controllers import DisplayToClipboard, AppendToClipboard

from mdk.utils.shared import format_bool, convert
from mdk.utils.expressions import check_types_assignable

def TriggerAnd(*exprs_: Expression | bool):
    ## auto-convert bools to BoolExpression.
    exprs = list(exprs_)
    for index in range(len(exprs)):
        expr = exprs[index]
        if type(expr) == bool: exprs[index] = format_bool(expr)

    ## check all exprs as input have bool type
    ## for compatibility we must treat Int as Bool.
    for expr in exprs:
        if not isinstance(expr, Expression):
            raise Exception(f"Expected input to AND statement to be convertible to an Expression, but found {type(expr)}.")
        if expr.type not in [BoolType, IntType, ShortType, ByteType, StateNoType]:
            if (not isinstance(expr.type, EnumType) and not isinstance(expr.type, FlagType)) or not expr.type.register:
                raise Exception(f"Expected input to AND statement to be an Expression with type `bool` or an equivalent type, not {expr.type.name}.")
        
    expr_string = " && ".join([expr.exprn for expr in exprs if isinstance(expr, Expression)])
    return Expression(f"({expr_string})", BoolType)

def TriggerOr(*exprs_: Expression | bool):
    ## auto-convert bools to BoolExpression.
    exprs = list(exprs_)
    for index in range(len(exprs)):
        expr = exprs[index]
        if type(expr) == bool: exprs[index] = format_bool(expr)

    ## check all exprs as input have bool type
    ## for compatibility we must treat Int as Bool.
    for expr in exprs:
        if not isinstance(expr, Expression):
            raise Exception(f"Expected input to OR statement to be convertible to an Expression, but found {type(expr)}.")
        if expr.type not in [BoolType, IntType, ShortType, ByteType, StateNoType]:
            if (not isinstance(expr.type, EnumType) and not isinstance(expr.type, FlagType)) or not expr.type.register:
                raise Exception(f"Expected input to OR statement to be an Expression with type `bool` or an equivalent type, not {expr.type.name}.")
        
    expr_string = " || ".join([expr.exprn for expr in exprs if isinstance(expr, Expression)])
    return Expression(f"({expr_string})", BoolType)

def TriggerNot(expr: Expression):
    ## auto-convert bools to BoolExpression.
    if type(expr) == bool:
        expr = format_bool(expr)

    """
    Note: this is intentionally disabled. In CNS, it is fine to do something like `!Life` to check when life is 0, but Life as an IntExpression
    would not work with this check. I think it's useful and natural to write `if not Life` in Python, so we can retain this CNS behaviour.

    if not isinstance(expr, BoolExpression):
        raise Exception(f"First parameter to NOT statement should be BoolExpression or BoolVar, not {type(expr)}.")
    """

    return Expression(f"!({expr.exprn})", BoolType)

def TriggerAssign(expr1: Expression, expr2: Expression):
    if not isinstance(expr1, VariableExpression):
        raise Exception(f"First parameter to assignment statement should be a VariableExpression, not {type(expr1)}.")
    if not isinstance(expr2, Expression):
        expr2 = convert(expr2)
    if check_types_assignable(expr1.type, expr2.type) == None:
        raise Exception(f"Inputs to assignment expression must have assignable types, not {expr1.type.name} and {expr2.type.name}.")

    return expr1.make_expression(f"({expr1.exprn} := {expr2.exprn})")

def TriggerPush():
    ctx = CompilerContext.instance()
    if not isinstance(ctx.current_trigger, Expression):
        ## it's legal for current_trigger to be None, it means the controller was called outside of an `if`.
        ## (i don't think it's possible for TriggerPush to invoke in this case, but better for safety).
        ctx.current_trigger = format_bool(True)
    ctx.trigger_stack.append(ctx.current_trigger)

def TriggerPop():
    ctx = CompilerContext.instance()
    if len(ctx.trigger_stack) == 0:
        raise Exception(f"Tried to pop triggers from an empty trigger stack.")
    ctx.trigger_stack.pop()

## this function is used if a bare `print` statement is found inside a `statedef`, `statefunc`, or `template`.
## it replaces the `print` with an appropriate `DisplayToClipboard`.
## this accepts an optional `append` kwarg, if this is set to `True` it will do AppendToClipboard instead.
def TriggerPrint(*args, **kwargs):
    ## before anything: if compile = False, just print normally
    if 'compile' in kwargs and kwargs['compile'] == False:
        print(*args)
        return

    ctx = CompilerContext.instance()
    if len(args) == 0: raise Exception("Must provide text input to convertible `print` statement.")

    if len(ctx.format_params) > 6:
        raise Exception("Convertible print statements and Clipboard controllers only support up to 6 parameters.")

    text: str = args[0]

    if 'end' in kwargs and kwargs['end'] != None:
        text += kwargs['end']

    ## handle formatting:
    ### - any % in the string becomes %%, UNLESS it matches a known type specifier.
    ### - any \ in the string becomes \\
    text = text.replace("\\", "\\\\").replace("%", "%%")
    text = text.replace("%%d", "%d").replace("%%f", "%f").replace("%%e", "%e").replace("%%E", "%E").replace("%%g", "%g").replace("%%G", "%G")

    if 'append' in kwargs and kwargs['append'] == True:
        AppendToClipboard(text = text, params = tuple(ctx.format_params) if len(ctx.format_params) > 0 else None)
    else:
        DisplayToClipboard(text = text, params = tuple(ctx.format_params) if len(ctx.format_params) > 0 else None)

    ctx.format_params = []