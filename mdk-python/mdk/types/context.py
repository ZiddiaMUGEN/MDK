from dataclasses import dataclass
from typing import Callable, Optional, Union

from mdk.types.triggers import TriggerException

class Expression:
    exprn: str
    def __init__(self, exprn: str):
        self.exprn = exprn
    def __repr__(self):
        return self.exprn
    def __str__(self):
        return self.exprn
    
    def make_expression(self, exprn: str):
        return Expression(exprn)
    
    ## comparisons
    def __eq__(self, other): # type: ignore
        ## allow eq/neq to check for None.
        if isinstance(self, Expression) and other == None:
            return False
        check_types_assignable(self, other)
        return BoolExpression(f"{self} = {other}")
    def __ne__(self, other): # type: ignore
        ## allow eq/neq to check for None.
        if isinstance(self, Expression) and other == None:
            return False
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
        return self.make_expression(f"{self} + {other}")
    def __sub__(self, other):
        check_types_assignable(self, other)
        return self.make_expression(f"{self} - {other}")
    def __mul__(self, other):
        check_types_assignable(self, other)
        return self.make_expression(f"{self} * {other}")
    def __truediv__(self, other):
        check_types_assignable(self, other)
        return self.make_expression(f"{self} / {other}")
    def __floordiv__(self, other):
        check_types_assignable(self, other)
        return self.make_expression(f"floor({self} / {other})")
    def __mod__(self, other):
        check_types_assignable(self, other)
        if not isinstance(self, IntExpression) and not isinstance(self, IntVar):
            raise Exception(f"Operands for the modulus operator must be integer, not {type(self)}.")
        if not isinstance(other, IntExpression) and not isinstance(other, IntVar):
            raise Exception(f"Operands for the modulus operator must be integer, not {type(other)}.")
        return IntExpression(f"{self} % {other}")
    def __pow__(self, other):
        check_types_assignable(self, other)
        return self.make_expression(f"{self} ** {other}")
    def __rshift__(self, other):
        raise Exception()
    def __lshift__(self, other):
        raise Exception()
    def __and__(self, other):
        check_types_assignable(self, other)
        return self.make_expression(f"{self} & {other}")
    def __or__(self, other):
        check_types_assignable(self, other)
        return self.make_expression(f"{self} | {other}")
    def __xor__(self, other):
        check_types_assignable(self, other)
        return self.make_expression(f"{self} ^ {other}")
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
        return self.make_expression(f"-({self})")
    def __pos__(self):
        return self.make_expression(f"+({self})")
    def __abs__(self):
        return self.make_expression(f"abs({self})")
    def __invert__(self):
        return self.make_expression(f"~({self})")
    def __round__(self):
        return self.make_expression(f"floor({self})")
    def __trunc__(self):
        return self.make_expression(f"floor({self})")
    def __floor__(self):
        return self.make_expression(f"floor({self})")
    def __ceil__(self):
        return self.make_expression(f"ceil({self})")
    
    # Trigger must ALWAYS be truthy, because any conditions a Trigger is used in should be TRUE to evaluate the statements below the condition.
    def __bool__(self):
        ## unfortunately this can't use mdk.utils.shared.get_context since that causes circular imports.
        ## but it can access the context itself here.
        ## we only need to set this expression onto TriggerStack when it is used as a bool.
        ctx = CompilerContext.instance
        ctx.current_trigger = self
        return True
    
def check_types_assignable(expr1: Expression, expr2: Expression):
    ## checks if the 2 expressions have a matching type.
    if isinstance(expr1, IntExpression) or isinstance(expr1, IntVar) or isinstance(expr1, int):
        if not isinstance(expr2, IntExpression) and not isinstance(expr2, IntVar) and not isinstance(expr2, int):
            raise Exception(f"Operands to operator must have compatible types; provided types are {type(expr1)} and {type(expr2)}.")
    if isinstance(expr1, FloatExpression) or isinstance(expr1, FloatVar) or isinstance(expr1, float):
        if not isinstance(expr2, FloatExpression) and not isinstance(expr2, FloatVar) and not isinstance(expr2, float):
            raise Exception(f"Operands to operator must have compatible types; provided types are {type(expr1)} and {type(expr2)}.")
    if isinstance(expr1, BoolExpression) or isinstance(expr1, BoolVar) or isinstance(expr1, bool):
        if not isinstance(expr2, BoolExpression) and not isinstance(expr2, BoolVar) and not isinstance(expr2, bool):
            raise Exception(f"Operands to operator must have compatible types; provided types are {type(expr1)} and {type(expr2)}.")

class VariableExpression(Expression):
    def __init__(self, name: str = ""):
        self.exprn = name

    def make_expression(self, exprn: str):
        return Expression(exprn)

class IntVar(VariableExpression):
    def __init__(self, name: str = ""):
        self.exprn = name

    def make_expression(self, exprn: str):
        return IntExpression(exprn)

class FloatVar(VariableExpression):
    def __init__(self, name: str = ""):
        self.exprn = name

    def make_expression(self, exprn: str):
        return FloatExpression(exprn)

class BoolVar(VariableExpression):
    def __init__(self, name: str = ""):
        self.exprn = name

    def make_expression(self, exprn: str):
        return BoolExpression(exprn)

class IntExpression(Expression):
    def __init__(self, exprn: Union[str, int, Expression]):
        super().__init__(str(exprn))

    def make_expression(self, exprn: str):
        return IntExpression(exprn)

class FloatExpression(Expression):
    def __init__(self, exprn: Union[str, float, Expression]):
        super().__init__(str(exprn))

    def make_expression(self, exprn: str):
        return FloatExpression(exprn)

class BoolExpression(Expression):
    def __init__(self, exprn: Union[str, bool, Expression]):
        if isinstance(exprn, bool):
            super().__init__("true" if exprn else "false")
        else:
            super().__init__(str(exprn))

    def make_expression(self, exprn: str):
        return BoolExpression(exprn)

class StringExpression(Expression):
    def __init__(self, exprn: str):
        if not isinstance(exprn, str):
            raise Exception("Input to a StringExpression must always be a constant string, not a different expression.")
        super().__init__(exprn)

    def make_expression(self, exprn: str):
        return StringExpression(exprn)

@dataclass
class StateController:
    type: str
    params: dict[str, Expression]
    triggers: list[Expression]

    def __init__(self):
        self.type = ""
        self.params = {}
        self.triggers = []

    def __repr__(self):
        result = "[State ]"
        result += f"\ntype = {self.type}"
        for trigger in self.triggers:
            result += f"\ntrigger1 = {trigger}"
        for param in self.params:
            result += f"\n{param} = {self.params[param]}"
        return result

@dataclass
class StateDefinition:
    fn: Callable
    params: dict[str, Expression]
    controllers: list[StateController]

@dataclass
class TemplateDefinition:
    fn: Callable
    library: Optional[str]
    params: dict[str, type]
    controllers: list[StateController]

@dataclass
class CompilerContext:
    statedefs: dict[str, StateDefinition]
    templates: dict[str, TemplateDefinition]
    current_state: Optional[StateDefinition]
    current_template: Optional[TemplateDefinition]
    current_trigger: Optional[Expression]
    trigger_stack: list[Expression]

    def __init__(self):
        self.statedefs = {}
        self.templates = {}
        self.current_state = None
        self.current_template = None
        self.current_trigger = None
        self.trigger_stack = []

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CompilerContext, cls).__new__(cls)
        return cls.instance
    
Int = IntExpression | IntVar
Float = FloatExpression | FloatVar
Bool = BoolExpression | BoolVar
String = StringExpression