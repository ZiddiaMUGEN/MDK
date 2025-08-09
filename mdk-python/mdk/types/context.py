from dataclasses import dataclass
from typing import Callable, Optional, Union
from enum import Enum
import traceback
import functools
import random
import string

from mdk.types.triggers import TriggerException

def generate_random_string(length: int):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

## this specifies a subset of the type categories provided by MTL.
class TypeCategory(Enum):
    #INVALID = -1
    #ALIAS = 0
    #UNION = 1
    ENUM = 2
    FLAG = 3
    STRUCTURE = 4
    #BUILTIN_STRUCTURE = 96 Note MDK does not need to differentiate between builtin and user-defined structs.
    #STRING_FLAG = 97 Note MDK does not need string flag/enum as it uses MTL for intermediate (where all enum/flag can be passed as string)
    #STRING_ENUM = 98
    BUILTIN = 99
    #BUILTIN_DENY = 100 Note MDK does not need to worry about BUILTIN_DENY as the MTL side can handle denying creation anyway.

## defines a generic type. this type is not intended for end-users, instead they should use a
## type specifier creation function (for user-defined enums, flags, and structs).
class TypeSpecifier:
    name: str
    category: TypeCategory
    def __init__(self, name: str, category: TypeCategory):
        self.name = name
        self.category = category

## these are builtin types which must be available to all characters.
IntType = TypeSpecifier("int", TypeCategory.BUILTIN)
FloatType = TypeSpecifier("float", TypeCategory.BUILTIN)
BoolType = TypeSpecifier("bool", TypeCategory.BUILTIN)
ShortType = TypeSpecifier("short", TypeCategory.BUILTIN)
ByteType = TypeSpecifier("byte", TypeCategory.BUILTIN)
CharType = TypeSpecifier("char", TypeCategory.BUILTIN)
StringType = TypeSpecifier("string", TypeCategory.BUILTIN)

StateNoType = TypeSpecifier("stateno", TypeCategory.BUILTIN)

def check_types_assignable(spec1: TypeSpecifier, spec2: TypeSpecifier) -> Optional[TypeSpecifier]:
    ## TODO: confirm the types are assignable, use the MDK spec type conversion rules.
    return None

## represents a structure member, mapping its field name to a type.
@dataclass
class StructureMember:
    name: str
    type: TypeSpecifier

class StructureType(TypeSpecifier):
    members: list[StructureMember]
    def __init__(self, name: str, category: TypeCategory, members: list[StructureMember]):
        self.name = name
        self.category = category
        self.members = members

class EnumType(TypeSpecifier):
    members: list[str]
    def __init__(self, name: str, category: TypeCategory, members: list[str]):
        self.name = name
        self.category = category
        self.members = members
    def __getattr__(self, name: str) -> 'Expression':
        for member in self.members:
            if member == name: return Expression(f"{self.name}.{member}", self)
        raise AttributeError(f"Member {name} does not exist on enum type {self.name}.")
    
class FlagType(TypeSpecifier):
    members: list[str]
    def __init__(self, name: str, category: TypeCategory, members: list[str]):
        self.name = name
        self.category = category
        self.members = members
    def __getattr__(self, name: str) -> 'Expression':
        all_members: list[str] = []
        for character in name:
            for member in self.members:
                if member == character: all_members.append(member)
            raise AttributeError(f"Member {character} does not exist on flag type {self.name}.")
        return Expression(f"{self.name}.{name}", self)

StateType = EnumType("StateType", TypeCategory.ENUM, ["S", "C", "A", "L", "U"])
MoveType = EnumType("MoveType", TypeCategory.ENUM, ["A", "I", "H", "U"])
PhysicsType = EnumType("PhysicsType", TypeCategory.ENUM, ["S", "C", "A", "N", "U"])

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
        ctx = CompilerContext.instance
        ctx.current_trigger = self
        return True

## these are helpers for specifying expressions for commonly-used built-in types.
IntExpression = functools.partial(Expression, type = IntType)

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
        context = CompilerContext.instance
        for frame in traceback.extract_stack():
            function_name = frame.name
            if function_name in context.statedefs or function_name in context.templates:
                ## means this is a line from a statedef or template function, so we should check the assignment
                if frame.line != None and len(frame.line.split("=")) == 2:
                    self.exprn = frame.line.split("=")[0].strip()
        
        ## if it could not be found, print a warning and assign a variable name.
        if context.current_state != None and self.exprn == "":
            self.exprn = f"_anon_{generate_random_string(8)}"
            print(f"Warning: Could not automatically identify the name of a variable in {context.current_state.fn.__name__}, assigning anonymous name {self.exprn}.")
        elif context.current_template != None and self.exprn == "":
            self.exprn = f"_anon_{generate_random_string(8)}"
            print(f"Warning: Could not automatically identify the name of a variable in {context.current_template.fn.__name__}, assigning anonymous name {self.exprn}.")

    def make_expression(self, exprn: str):
        return Expression(exprn, self.type)
    
## these are helpers for creating variables from commonly-used built-in types.
IntVar = functools.partial(VariableExpression, type = IntType)

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
    params: dict[str, TypeSpecifier]
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
