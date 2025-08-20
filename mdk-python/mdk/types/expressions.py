import functools
from typing import Union, Callable

from mdk.types.specifier import TypeSpecifier
from mdk.types.builtins import IntType, BoolType, FloatType, StringType, StateNoType
from mdk.types.context import CompilerContext, StateController

from mdk.utils.expressions import check_types_assignable

## this is just the 'convert' function from mdk.utils.shared,
## but copied here to avoid circular imports.
def _convert(input: Union['Expression', str, int, float, bool, Callable[..., StateController]]) -> 'Expression':
    if isinstance(input, Expression):
        return input
    elif isinstance(input, functools.partial):
        return Expression(input.keywords["value"], StateNoType)
    elif isinstance(input, Callable):
        return Expression(input.__name__, StateNoType)
    elif type(input) == str:
        return Expression(input, StringType)
    elif type(input) == int:
        return Expression(str(input), IntType)
    elif type(input) == float:
        return Expression(str(input), FloatType)
    elif type(input) == bool:
        return Expression("true" if input else "false", BoolType)
    else:
        raise Exception(f"Attempted to convert from unsupported builtin type {type(input)}.")

## an Expression is a core component of building CNS.
## Expressions represent all trigger expressions, parameter expressions, etc.
class Expression:
    exprn: str
    type: TypeSpecifier
    def __init__(self, exprn: str, type: TypeSpecifier):
        self.exprn = exprn
        self.type = type
    def __repr__(self):
        return self.exprn
    def __str__(self):
        if self.type == StringType:
            return f'"{self.exprn}"'
        return self.exprn
    
    def make_expression(self, exprn: str):
        return Expression(exprn, self.type)
    
    ## comparisons
    def __eq__(self, other): # type: ignore
        if other is None:
            return NotImplemented
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"({self} = {other})", BoolType)
    def __ne__(self, other): # type: ignore
        if other is None:
            return NotImplemented
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"({self} != {other})", BoolType)
    def __lt__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"({self} < {other})", BoolType)
    def __le__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"({self} <= {other})", BoolType)
    def __gt__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"({self} > {other})", BoolType)
    def __ge__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"({self} >= {other})", BoolType)
    
    ## mathematical operations
    def __add__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be added.")
        return Expression(f"({self} + {other})", self.type)
    def __sub__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be subtracted.")
        return Expression(f"({self} - {other})", self.type)
    def __mul__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be multiplied.")
        return Expression(f"({self} * {other})", self.type)
    def __truediv__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be divided.")
        return Expression(f"({self} / {other})", self.type)
    def __floordiv__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be divided.")
        return Expression(f"floor({self} / {other})", self.type)
    def __mod__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have modulus taken.")
        ## TODO: confirm the input types are both `int` or assignable to `int`
        return Expression(f"({self} % {other})", IntType)
    def __pow__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have exponentiation taken.")
        return Expression(f"({self} ** {other})", self.type)
    def __rshift__(self, other):
        raise Exception()
    def __lshift__(self, other):
        raise Exception()
    def __and__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have bitwise and taken.")
        return Expression(f"({self} & {other})", self.type)
    def __or__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have bitwise or taken.")
        return Expression(f"({self} | {other})", self.type)
    def __xor__(self, other):
        if not isinstance(other, Expression):
            other = _convert(other)
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have bitwise xor taken.")
        return Expression(f"({self} ^ {other})", self.type)
    def __radd__(self, other): return self.__add__(other)
    def __rsub__(self, other): return self.__sub__(other)
    def __rmul__(self, other): return self.__mul__(other)
    def __rtruediv__(self, other): return self.__truediv__(other)
    def __rfloordiv__(self, other): return self.__floordiv__(other)
    def __rmod__(self, other): return self.__mod__(other)
    def __rpow__(self, other): return self.__pow__(other)
    def __rlshift__(self, other): return self.__lshift__(other)
    def __rrshift__(self, other): return self.__rshift__(other)
    def __rand__(self, other): return self.__and__(other)
    def __ror__(self, other): return self.__or__(other)
    def __rxor__(self, other): return self.__xor__(other)
    def __neg__(self):
        return Expression(f"-({self})", self.type)
    def __pos__(self):
        return Expression(f"+({self})", self.type)
    def __abs__(self):
        return Expression(f"abs({self})", self.type)
    def __invert__(self):
        return Expression(f"~({self})", self.type)
    def __round__(self):
        return Expression(f"floor({self})", self.type)
    def __trunc__(self):
        return Expression(f"floor({self})", self.type)
    def __floor__(self):
        return Expression(f"floor({self})", self.type)
    def __ceil__(self):
        return Expression(f"ceil({self})", self.type)
    
    def __bool__(self):
        ctx = CompilerContext.instance()
        ctx.current_trigger = Expression(self.exprn, self.type)
        return True
    
## these are helpers for specifying expressions for commonly-used built-in types.
IntExpression = functools.partial(Expression, type = IntType)

## type hint for a tuple with variable length
type ConvertibleExpression = Union[Expression, str, int, float, bool]
type TupleExpression = tuple[ConvertibleExpression, ...]

__all__ = ["Expression", "IntExpression", "ConvertibleExpression", "TupleExpression"]