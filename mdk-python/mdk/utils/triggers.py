from mdk.types.context import Expression, VariableExpression, IntExpression, FloatExpression, BoolExpression, IntVar, FloatVar, BoolVar
from mdk.types.triggers import TriggerException

from mdk.utils.shared import get_context

def TriggerAnd(expr1: Expression, expr2: Expression, filename: str, line: int):
    ## auto-convert bools to BoolExpression.
    if isinstance(expr1, bool):
        expr1 = BoolExpression(expr1)
    if isinstance(expr2, bool):
        expr2 = BoolExpression(expr2)

    if not isinstance(expr1, BoolExpression) and not isinstance(expr1, BoolVar):
        raise TriggerException(f"First parameter to AND statement should be BoolExpression or BoolVar, not {type(expr1)}.", filename, line)
    if not isinstance(expr2, BoolExpression) and not isinstance(expr2, BoolVar):
        raise TriggerException(f"Second parameter to AND statement should be BoolExpression or BoolVar, not {type(expr2)}.", filename, line)

    return BoolExpression(f"{expr1.exprn} && {expr2.exprn}")

def TriggerOr(expr1: Expression, expr2: Expression, filename: str, line: int):
    ## auto-convert bools to BoolExpression.
    if isinstance(expr1, bool):
        expr1 = BoolExpression(expr1)
    if isinstance(expr2, bool):
        expr2 = BoolExpression(expr2)

    if not isinstance(expr1, BoolExpression) and not isinstance(expr1, BoolVar):
        raise TriggerException(f"First parameter to OR statement should be BoolExpression or BoolVar, not {type(expr1)}.", filename, line)
    if not isinstance(expr2, BoolExpression) and not isinstance(expr2, BoolVar):
        raise TriggerException(f"Second parameter to OR statement should be BoolExpression or BoolVar, not {type(expr2)}.", filename, line)

    return BoolExpression(f"{expr1.exprn} || {expr2.exprn}")

def TriggerNot(expr: Expression, filename: str, line: int):
    ## auto-convert bools to BoolExpression.
    if isinstance(expr, bool):
        expr = BoolExpression(expr)

    """
    Note: this is intentionally disabled. In CNS, it is fine to do something like `!Life` to check when life is 0, but Life as an IntExpression
    would not work with this check. I think it's useful and natural to write `if not Life` in Python, so we can retain this CNS behaviour.

    if not isinstance(expr, BoolExpression):
        raise TriggerException(f"First parameter to NOT statement should be BoolExpression or BoolVar, not {type(expr)}.", filename, line)
    """

    return BoolExpression(f"!({expr.exprn})")

def TriggerAssign(expr1: Expression, expr2: Expression, filename: str, line: int):
    if not isinstance(expr1, VariableExpression):
        raise TriggerException(f"First parameter to assignment statement should be a VariableExpression, not {type(expr1)}.", filename, line)
    if isinstance(expr1, IntVar):
        if not isinstance(expr2, IntVar) and not isinstance(expr2, IntExpression):
            raise TriggerException(f"Second parameter to assignment statement for IntVar should be IntVar or IntExpression, not {type(expr2)}.", filename, line)
    if isinstance(expr1, FloatVar):
        if not isinstance(expr2, FloatVar) and not isinstance(expr2, FloatExpression):
            raise TriggerException(f"Second parameter to assignment statement for FloatVar should be FloatVar or FloatExpression, not {type(expr2)}.", filename, line)
    if isinstance(expr1, BoolVar):
        if not isinstance(expr2, BoolVar) and not isinstance(expr2, BoolExpression):
            raise TriggerException(f"Second parameter to assignment statement for BoolVar should be BoolVar or BoolExpression, not {type(expr2)}.", filename, line)

    return expr1.make_expression(f"{expr1.exprn} := {expr2.exprn}")

def TriggerPush(file: str, line: int):
    ctx = get_context()
    if not isinstance(ctx.current_trigger, Expression):
        ## it's legal for current_trigger to be None, it means the controller was called outside of an `if`.
        ## (i don't think it's possible for TriggerPush to invoke in this case, but better for safety).
        ctx.current_trigger = BoolExpression(True)
    ctx.trigger_stack.append(ctx.current_trigger)

def TriggerPop(file: str, line: int):
    ctx = get_context()
    if len(ctx.trigger_stack) == 0:
        raise TriggerException(f"Tried to pop triggers from an empty trigger stack.", file, line)
    ctx.trigger_stack.pop()