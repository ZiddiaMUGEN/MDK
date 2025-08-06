from typing import Union
from enum import Enum
from dataclasses import dataclass

## enums for types
class StateType(Enum):
    S = 0
    C = 1
    A = 2
    L = 3
    U = 4

class MoveType(Enum):
    I = 0
    A = 1
    H = 2
    U = 3

class PhysicsType(Enum):
    S = 0
    C = 1
    A = 2
    N = 3
    U = 4

class Transparency(Enum):
    none = 0, ## casing sucks here but None is a reserved word.
    Add = 1,
    Add1 = 2,
    Sub = 3

class VarScope(Enum):
    Local = 0,
    Global = 1

def check_types_assignable(expr1: 'Expression', expr2: 'Expression'):
    ## checks if the 2 expressions have a matching type.
    if isinstance(expr1, IntExpression) or isinstance(expr1, IntVar):
        if not isinstance(expr2, IntExpression) and not isinstance(expr2, IntVar):
            raise Exception(f"Operands to operator must have compatible types; provided types are {type(expr1)} and {type(expr2)}.")
    if isinstance(expr1, FloatExpression) or isinstance(expr1, FloatVar):
        if not isinstance(expr2, FloatExpression) and not isinstance(expr2, FloatVar):
            raise Exception(f"Operands to operator must have compatible types; provided types are {type(expr1)} and {type(expr2)}.")
    if isinstance(expr1, BoolExpression) or isinstance(expr1, BoolVar):
        if not isinstance(expr2, BoolExpression) and not isinstance(expr2, BoolVar):
            raise Exception(f"Operands to operator must have compatible types; provided types are {type(expr1)} and {type(expr2)}.")

@dataclass
class Expression:
    exprn: str
    def __init__(self, exprn: str):
        self.exprn = exprn
    def __repr__(self):
        return self.exprn
    def __str__(self):
        return self.exprn
    
    ## comparisons
    def __eq__(self, other): # type: ignore
        check_types_assignable(self, other)
        return BoolExpression(f"{self} = {other}")
    def __ne__(self, other): # type: ignore
        check_types_assignable(self, other)
        return BoolExpression(f"{self} != {other}")
    def __lt__(self, other):
        check_types_assignable(self, other)
        return BoolExpression(f"{self} < {other}")
    def __lte__(self, other):
        check_types_assignable(self, other)
        return BoolExpression(f"{self} <= {other}")
    def __gt__(self, other):
        check_types_assignable(self, other)
        return BoolExpression(f"{self} > {other}")
    def __gte__(self, other):
        check_types_assignable(self, other)
        return BoolExpression(f"{self} >= {other}")
    
    ## mathematical operations
    def __add__(self, other):
        check_types_assignable(self, other)
        return self.__class__(f"{self} + {other}")
    def __sub__(self, other):
        check_types_assignable(self, other)
        return self.__class__(f"{self} - {other}")
    def __mul__(self, other):
        check_types_assignable(self, other)
        return self.__class__(f"{self} * {other}")
    def __truediv__(self, other):
        check_types_assignable(self, other)
        return self.__class__(f"{self} / {other}")
    def __floordiv__(self, other):
        check_types_assignable(self, other)
        return self.__class__(f"floor({self} / {other})")
    def __mod__(self, other):
        check_types_assignable(self, other)
        if not isinstance(self, IntExpression) and not isinstance(self, IntVar):
            raise Exception(f"Operands for the modulus operator must be integer, not {type(self)}.")
        if not isinstance(other, IntExpression) and not isinstance(other, IntVar):
            raise Exception(f"Operands for the modulus operator must be integer, not {type(other)}.")
        return IntExpression(f"{self} % {other}")
    def __pow__(self, other):
        check_types_assignable(self, other)
        return self.__class__(f"{self} ** {other}")
    def __rshift__(self, other):
        raise Exception()
    def __lshift__(self, other):
        raise Exception()
    def __and__(self, other):
        check_types_assignable(self, other)
        return self.__class__(f"{self} & {other}")
    def __or__(self, other):
        check_types_assignable(self, other)
        return self.__class__(f"{self} | {other}")
    def __xor__(self, other):
        check_types_assignable(self, other)
        return self.__class__(f"{self} ^ {other}")
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
        return self.__class__(f"-({self})")
    def __pos__(self):
        return self.__class__(f"+({self})")
    def __abs__(self):
        return self.__class__(f"abs({self})")
    def __invert__(self):
        return self.__class__(f"~({self})")
    def __round__(self):
        return self.__class__(f"floor({self})")
    def __trunc__(self):
        return self.__class__(f"floor({self})")
    def __floor__(self):
        return self.__class__(f"floor({self})")
    def __ceil__(self):
        return self.__class__(f"ceil({self})")
    
    # Trigger must ALWAYS be truthy, because any conditions a Trigger is used in should be TRUE to evaluate the statements below the condition.
    def __bool__(self):
        return True

@dataclass
class VariableExpression(Expression):
    def __init__(self, name: str = ""):
        self.exprn = name

@dataclass
class IntVar(VariableExpression):
    def __init__(self, name: str = ""):
        self.exprn = name

@dataclass
class FloatVar(VariableExpression):
    def __init__(self, name: str = ""):
        self.exprn = name

@dataclass
class BoolVar(VariableExpression):
    def __init__(self, name: str = ""):
        self.exprn = name

@dataclass
class IntExpression(Expression):
    def __init__(self, exprn: Union[str, int, Expression]):
        super().__init__(str(exprn))

@dataclass
class FloatExpression(Expression):
    def __init__(self, exprn: Union[str, float, Expression]):
        super().__init__(str(exprn))

@dataclass
class BoolExpression(Expression):
    def __init__(self, exprn: Union[str, bool, Expression]):
        if isinstance(exprn, bool):
            super().__init__("true" if exprn else "false")
        else:
            super().__init__(str(exprn))