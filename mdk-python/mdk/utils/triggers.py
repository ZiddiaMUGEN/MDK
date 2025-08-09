from mdk.types.context import Expression, VariableExpression, BoolType, check_types_assignable
from mdk.types.triggers import TriggerException

from mdk.utils.shared import get_context, format_bool

def TriggerAnd(expr1: Expression, expr2: Expression, filename: str, line: int):
    ## auto-convert bools to BoolExpression.
    if isinstance(expr1, bool):
        expr1 = format_bool(expr1)
    if isinstance(expr2, bool):
        expr2 = format_bool(expr2)

    if expr1.type != BoolType:
        raise TriggerException(f"First parameter to AND statement should have type `bool`, not {expr1.type.name}.", filename, line)
    if expr2.type != BoolType:
        raise TriggerException(f"Second parameter to AND statement should have type `bool`, not {expr2.type.name}.", filename, line)

    return Expression(f"{expr1.exprn} && {expr2.exprn}", BoolType)

def TriggerOr(expr1: Expression, expr2: Expression, filename: str, line: int):
    ## auto-convert bools to BoolExpression.
    if isinstance(expr1, bool):
        expr1 = format_bool(expr1)
    if isinstance(expr2, bool):
        expr2 = format_bool(expr2)

    if expr1.type != BoolType:
        raise TriggerException(f"First parameter to OR statement should have type `bool`, not {expr1.type.name}.", filename, line)
    if expr2.type != BoolType:
        raise TriggerException(f"Second parameter to OR statement should have type `bool`, not {expr2.type.name}.", filename, line)

    return Expression(f"{expr1.exprn} || {expr2.exprn}", BoolType)

def TriggerNot(expr: Expression, filename: str, line: int):
    ## auto-convert bools to BoolExpression.
    if isinstance(expr, bool):
        expr = format_bool(expr)

    """
    Note: this is intentionally disabled. In CNS, it is fine to do something like `!Life` to check when life is 0, but Life as an IntExpression
    would not work with this check. I think it's useful and natural to write `if not Life` in Python, so we can retain this CNS behaviour.

    if not isinstance(expr, BoolExpression):
        raise TriggerException(f"First parameter to NOT statement should be BoolExpression or BoolVar, not {type(expr)}.", filename, line)
    """

    return Expression(f"!({expr.exprn})", BoolType)

def TriggerAssign(expr1: Expression, expr2: Expression, filename: str, line: int):
    if not isinstance(expr1, VariableExpression):
        raise TriggerException(f"First parameter to assignment statement should be a VariableExpression, not {type(expr1)}.", filename, line)
    if check_types_assignable(expr1.type, expr2.type) == None:
        raise TriggerException(f"Inputs to assignment expression must have assignable types, not {expr1.type.name} and {expr2.type.name}.", filename, line)

    return expr1.make_expression(f"{expr1.exprn} := {expr2.exprn}")

def TriggerPush(file: str, line: int):
    ctx = get_context()
    if not isinstance(ctx.current_trigger, Expression):
        ## it's legal for current_trigger to be None, it means the controller was called outside of an `if`.
        ## (i don't think it's possible for TriggerPush to invoke in this case, but better for safety).
        ctx.current_trigger = format_bool(True)
    ctx.trigger_stack.append(ctx.current_trigger)

def TriggerPop(file: str, line: int):
    ctx = get_context()
    if len(ctx.trigger_stack) == 0:
        raise TriggerException(f"Tried to pop triggers from an empty trigger stack.", file, line)
    ctx.trigger_stack.pop()