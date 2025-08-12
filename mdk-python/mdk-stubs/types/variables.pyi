from mdk.types.expressions import ConvertibleExpression, Expression
from mdk.types.specifier import TypeSpecifier

__all__ = ['VariableExpression', 'IntVar', 'FloatVar']

class VariableExpression(Expression):
    type: TypeSpecifier
    exprn: str
    def __init__(self, type: TypeSpecifier) -> None: ...
    def make_expression(self, exprn: str): ...
    def set(self, val: ConvertibleExpression): ...
    def add(self, val: ConvertibleExpression): ...

IntVar: VariableExpression
FloatVar: VariableExpression
