import functools
from enum import Enum

from mdk.types.specifier import TypeSpecifier, IntType, BoolType

from mdk.utils.expressions import check_types_assignable
from mdk.utils.shared import generate_random_string

class ScopeType(Enum):
    SHARED = 0
    PLAYER = 1
    HELPER = 2
    TARGET = 3

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
        return self.exprn
    
    def make_expression(self, exprn: str):
        return Expression(exprn, self.type)
    
    ## comparisons
    def __eq__(self, other): # type: ignore
        ## allow eq/neq to check for None.
        if not isinstance(other, Expression):
            return NotImplemented
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"{self} = {other}", BoolType)
    def __ne__(self, other): # type: ignore
        ## allow eq/neq to check for None.
        if not isinstance(other, Expression):
            return NotImplemented
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"{self} != {other}", BoolType)
    def __lt__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"{self} < {other}", BoolType)
    def __lte__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"{self} <= {other}", BoolType)
    def __gt__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"{self} > {other}", BoolType)
    def __gte__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be compared.")
        return Expression(f"{self} >= {other}", BoolType)
    
    ## mathematical operations
    def __add__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be added.")
        return Expression(f"{self} + {other}", self.type)
    def __sub__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be subtracted.")
        return Expression(f"{self} - {other}", self.type)
    def __mul__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be multiplied.")
        return Expression(f"{self} * {other}", self.type)
    def __truediv__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be divided.")
        return Expression(f"{self} / {other}", self.type)
    def __floordiv__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot be divided.")
        return Expression(f"floor({self} / {other})", self.type)
    def __mod__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have modulus taken.")
        ## TODO: confirm the input types are both `int` or assignable to `int`
        return Expression(f"{self} % {other}", IntType)
    def __pow__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have exponentiation taken.")
        return Expression(f"{self} ** {other}", self.type)
    def __rshift__(self, other):
        raise Exception()
    def __lshift__(self, other):
        raise Exception()
    def __and__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have bitwise and taken.")
        return Expression(f"{self} & {other}", self.type)
    def __or__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have bitwise or taken.")
        return Expression(f"{self} | {other}", self.type)
    def __xor__(self, other):
        if check_types_assignable(self.type, other.type) == None:
            raise Exception(f"Types {self.type.name} and {other.type.name} are not assignable and cannot have bitwise xor taken.")
        return Expression(f"{self} ^ {other}", self.type)
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

## these are helpers for specifying expressions for commonly-used built-in types.
IntExpression = functools.partial(Expression, type = IntType)