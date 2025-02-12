## base class for triggers, defines some operator overloads.
## basically any operators on a Trigger should NOT have an effect and instead should generate code.
from mdk.utils import debug
from mdk import state

## generic trigger. overrides operators to implement code generation.
class Trigger:
    def __init__(self, repr: str):
        self.repr: str = repr
        state.CURRENT_EXPRESSION = repr
    def __str__(self):
        return self.repr
    
    ## comparisons
    def __eq__(self, other):
        debug(f"comparison check: {self} = {other}")
        return Trigger(f"{self} = {other}")
    def __ne__(self, other):
        debug(f"comparison check: {self} != {other}")
        return Trigger(f"{self} != {other}")
    def __lt__(self, other):
        debug(f"comparison check: {self} < {other}")
        return Trigger(f"{self} < {other}")
    def __lte__(self, other):
        debug(f"comparison check: {self} <= {other}")
        return Trigger(f"{self} <= {other}")
    def __gt__(self, other):
        debug(f"comparison check: {self} > {other}")
        return Trigger(f"{self} > {other}")
    def __gte__(self, other):
        debug(f"comparison check: {self} >= {other}")
        return Trigger(f"{self} >= {other}")
    
    ## mathematical operations
    def __add__(self, other):
        debug(f"mathematical op: {self} + {other}")
        return Trigger(f"{self} + {other}")
    def __sub__(self, other):
        debug(f"mathematical op: {self} - {other}")
        return Trigger(f"{self} - {other}")
    def __mul__(self, other):
        debug(f"mathematical op: {self} * {other}")
        return Trigger(f"{self} * {other}")
    def __truediv__(self, other):
        debug(f"mathematical op: {self} / {other}")
        return Trigger(f"{self} / {other}")
    def __floordiv__(self, other):
        debug(f"mathematical op: {self} // {other}")
        return Trigger(f"floor({self} / {other})")
    def __mod__(self, other):
        debug(f"mathematical op: {self} % {other}")
        return Trigger(f"{self} % {other}")
    def __pow__(self, other):
        debug(f"mathematical op: {self} ** {other}")
        return Trigger(f"{self} ** {other}")
    def __rshift__(self, other):
        debug(f"mathematical op: {self} >> {other}")
        ## TODO: this needs to be verified for correctness.
        return Trigger(f"({self} & 2147483647) / (2 ** {other}) | ifelse({self} < 0, 2 ** (31 - {other}), 0)")
    def __lshift__(self, other):
        debug(f"mathematical op: {self} << {other}")
        ## TODO: this needs to be verified for correctness.
        return Trigger(f"({self} & 2147483647) * (2 ** {other})")
    def __and__(self, other):
        debug(f"mathematical op: {self} & {other}")
        return Trigger(f"{self} & {other}")
    def __or__(self, other):
        debug(f"mathematical op: {self} | {other}")
        return Trigger(f"{self} | {other}")
    def __xor__(self, other):
        debug(f"mathematical op: {self} ^ {other}")
        return Trigger(f"{self} ^ {other}")
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
        debug(f"mathematical op: -{self}")
        return Trigger(f"-({self})")
    def __pos__(self):
        debug(f"mathematical op: +{self}")
        return Trigger(f"+({self})")
    def __abs__(self):
        debug(f"mathematical op: abs({self})")
        return Trigger(f"abs({self})")
    def __invert__(self):
        debug(f"mathematical op: ~{self}")
        return Trigger(f"~({self})")
    def __round__(self):
        debug(f"mathematical op: round({self})")
        return Trigger(f"floor({self})")
    def __trunc__(self):
        debug(f"mathematical op: trunc({self})")
        return Trigger(f"floor({self})")
    def __floor__(self):
        debug(f"mathematical op: floor({self})")
        return Trigger(f"floor({self})")
    def __ceil__(self):
        debug(f"mathematical op: ceil({self})")
        return Trigger(f"ceil({self})")
    
    # Trigger must ALWAYS be truthy, because any conditions a Trigger is used in should be TRUE to evaluate the statements below the condition.
    def __bool__(self):
        return True
    
## overriding logical operator functions.
def TriggerAnd(*args):
    # we only need to codegen if there is at least 1 argument which evals to Trigger.
    should_codegen = any(isinstance(arg, Trigger) for arg in args)
    # if not codegenning, just return logical AND of the arguments.
    if not should_codegen: return all(args)
    # if codegenning, this MUST return a Trigger to codegen for the controllers inside the statement.
    # the trigger will have a representation for the actual CNS trigger, and is always truthy.
    repr = []
    for arg in args:
        repr.append(str(arg))
    repr = f"({' && '.join(repr)})"
    debug(f"logical op: {repr}")
    return Trigger(repr)

def TriggerOr(*args):
    # we only need to codegen if there is at least 1 argument which evals to Trigger.
    should_codegen = any(isinstance(arg, Trigger) for arg in args)
    # if not codegenning, just return logical OR of the arguments.
    if not should_codegen: return any(args)
    # if codegenning, this MUST return a Trigger to codegen for the controllers inside the statement.
    # the trigger will have a representation for the actual CNS trigger, and is always truthy.
    repr = []
    for arg in args:
        repr.append(str(arg))
    repr = f"({' || '.join(repr)})"
    debug(f"logical op: {repr}")
    return Trigger(repr)

def TriggerNot(first):
    # we only need to codegen if there is at least 1 argument which evals to Trigger.
    should_codegen = isinstance(first, Trigger)
    # if not codegenning, just return logical OR of the arguments.
    if not should_codegen: return not first
    # if codegenning, this MUST return a Trigger to codegen for the controllers inside the statement.
    # the trigger will have a representation for the actual CNS trigger, and is always truthy.
    repr = f"!{first}"
    debug(f"logical op: {repr}")
    return Trigger(repr)

## individual triggers exposed by MUGEN.
Anim = Trigger("Anim")
AnimTime = Trigger("AnimTime")
Time = Trigger("Time")