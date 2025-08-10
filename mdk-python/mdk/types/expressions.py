import functools
from enum import Enum
import traceback

from mdk.types.specifier import TypeSpecifier, IntType, FloatType, BoolType
from mdk.types.context import CompilerContext, ParameterDefinition

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
    
    # Trigger must ALWAYS be truthy, because any conditions a Trigger is used in should be TRUE to evaluate the statements below the condition.
    def __bool__(self):
        ## unfortunately this can't use mdk.utils.shared.get_context since that causes circular imports.
        ## but it can access the context itself here.
        ## we only need to set this expression onto TriggerStack when it is used as a bool.
        ctx = CompilerContext.instance()
        ctx.current_trigger = self
        return True
    
## a special type of Expression which represents a variable access.
## generally speaking this is just treated differently so that we can
## detect variable initialization and scope in the state/template code.
class VariableExpression(Expression):
    def __init__(self, type: TypeSpecifier):
        self.type = type
        self.exprn = ""

        ## in order to determine a name for this variable, we need to walk through the backtrace
        ## and find calling code which originates from a statedef or template function, or
        ## from the top level of a module (other than this one).
        context = CompilerContext.instance()
        traceback.extract_tb(None)
        for frame in traceback.extract_stack():
            function_name = frame.name
            if function_name in context.statedefs and frame.line != None and len(frame.line.split("=")) == 2:
                ## means this is a line from a statedef or template function, so we should check the assignment
                self.exprn = frame.line.split("=")[0].strip()
                if next(filter(lambda k: k.name == self.exprn, context.statedefs[function_name].locals), None) != None:
                    raise Exception(f"Attempted to create 2 local variables with the same name {self.exprn} in state definition {function_name}.")
                context.statedefs[function_name].locals.append(ParameterDefinition(self.type, self.exprn))
                break
            elif function_name in context.templates and frame.line != None and len(frame.line.split("=")) == 2:
                ## means this is a line from a statedef or template function, so we should check the assignment
                self.exprn = frame.line.split("=")[0].strip()
                if next(filter(lambda k: k.name == self.exprn, context.templates[function_name].locals), None) != None:
                    raise Exception(f"Attempted to create 2 local variables with the same name {self.exprn} in template definition {function_name}.")
                context.templates[function_name].locals.append(ParameterDefinition(self.type, self.exprn))
            elif context.current_state == None and context.current_template == None and function_name == "<module>" and frame.line != None and len(frame.line.split("=")) == 2:
                ## means this is a line from a global scope
                self.exprn = frame.line.split("=")[0].strip()
                if next(filter(lambda k: k.name == self.exprn, context.globals), None) != None:
                    raise Exception(f"Attempted to create 2 global variables with the same name {self.exprn}.")
                context.globals.append(ParameterDefinition(self.type, self.exprn))
        
        ## if it could not be found, print a warning and assign a variable name.
        if context.current_state != None and self.exprn == "":
            self.exprn = f"_anon_{generate_random_string(8)}"
            print(f"Warning: Could not automatically identify the name of a variable in {context.current_state.fn.__name__}, assigning anonymous name {self.exprn}.")
        elif context.current_template != None and self.exprn == "":
            self.exprn = f"_anon_{generate_random_string(8)}"
            print(f"Warning: Could not automatically identify the name of a variable in {context.current_template.fn.__name__}, assigning anonymous name {self.exprn}.")
        elif context.current_template == None and context.current_state == None and self.exprn == "":
            self.exprn = f"_anon_{generate_random_string(8)}"
            print(f"Warning: Could not automatically identify the name of a variable in global state, assigning anonymous name {self.exprn}.")

    def make_expression(self, exprn: str):
        return Expression(exprn, self.type)

## these are helpers for specifying expressions for commonly-used built-in types.
IntExpression = functools.partial(Expression, type = IntType)

## these are helpers for creating variables from commonly-used built-in types.
IntVar = functools.partial(VariableExpression, type = IntType)
FloatVar = functools.partial(VariableExpression, type = FloatType)