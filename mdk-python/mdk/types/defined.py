from dataclasses import dataclass
from enum import Enum, Flag
from typing import Union, Optional

from mdk.types.specifier import TypeCategory, TypeSpecifier
from mdk.types.builtins import *
from mdk.types.expressions import Expression
from mdk.types.context import CompilerContext
from mdk.types.enums import *

## represents a structure member, mapping its field name to a type.
@dataclass
class StructureMember:
    name: str
    type: TypeSpecifier

class StructureType(TypeSpecifier):
    members: list[StructureMember]
    def __init__(self, name: str, members: list[StructureMember], register: bool = True, library: str | None = None):
        self.name = name
        self.category = TypeCategory.STRUCTURE
        self.members = members
        self.register = register

        context = CompilerContext.instance()
        if self.name in context.typedefs:
            raise Exception(f"A type with name {self.name} was already registered.")
        context.typedefs[self.name] = self

        self.library = library

class EnumType(TypeSpecifier):
    members: list[str]
    inner_type: Optional[type[Enum]]
    def __init__(self, name: str, members: Union[list[str], type[Enum]], register: bool = True, library: str | None = None):
        self.name = name
        self.category = TypeCategory.ENUM
        if isinstance(members, list):
            self.members = members
            self.inner_type = None
        else:
            self.members = members._member_names_
            self.inner_type = members
        self.register = register

        context = CompilerContext.instance()
        if self.name in context.typedefs:
            raise Exception(f"A type with name {self.name} was already registered.")
        context.typedefs[self.name] = self

        self.library = library

    def __deepcopy__(self, memo):
        return self

    def __getattr__(self, name: str) -> Expression:
        for member in self.members:
            if member == name: return Expression(f"{self.name}.{member}", self)
        raise AttributeError(f"Member {name} does not exist on enum type {self.name}.")
    
class FlagType(TypeSpecifier):
    members: list[str]
    inner_type: Optional[type[Flag]]
    def __init__(self, name: str, members: Union[list[str], type[Flag]], register: bool = True, library: str | None = None):
        self.name = name
        self.category = TypeCategory.FLAG
        if isinstance(members, list):
            self.members = members
            self.inner_type = None
        else:
            self.members = members._member_names_
            self.inner_type = members 
        self.register = register

        context = CompilerContext.instance()
        if self.name in context.typedefs:
            raise Exception(f"A type with name {self.name} was already registered.")
        context.typedefs[self.name] = self

        self.library = library

    def __deepcopy__(self, memo):
        return self

    def __getattr__(self, name: str) -> Expression:
        all_members: list[str] = []

        ## 'full' flag with whole members
        if name in self.members:
            return Expression(f"{self.name}.{name}", self)
        
        for character in name:
            found = False
            for member in self.members:
                if member == character: 
                    all_members.append(member)
                    found = True
                    break
            if not found:
                raise AttributeError(f"Member {character} does not exist on flag type {self.name}.")

        return Expression(f"{self.name}.{name}", self)
    
class TupleType(TypeSpecifier):
    members: list[TypeSpecifier]
    def __init__(self, name: str, category: TypeCategory, members: list[TypeSpecifier]):
        self.name = name
        self.category = category
        self.members = members

StateTypeT = EnumType("StateType", StateType, register = False)
MoveTypeT = EnumType("MoveType", MoveType, register = False)
PhysicsTypeT = EnumType("PhysicsType", PhysicsType, register = False)

HitTypeF = FlagType("HitType", HitType, register = False)
HitAttrF = FlagType("HitAttr", HitAttr, register = False)

TransTypeT = EnumType("TransType", TransType, register = False)
AssertTypeT = EnumType("AssertType", AssertType, register = False)
WaveTypeT = EnumType("WaveType", WaveType, register = False)
HelperTypeT = EnumType("HelperType", HelperType, register = False)
TeamTypeT = EnumType("TeamType", TeamType, register = False)
HitAnimTypeT = EnumType("HitAnimType", HitAnimType, register = False)
AttackTypeT = EnumType("AttackType", AttackType, register = False)
PriorityTypeT = EnumType("PriorityType", PriorityType, register = False)
PosTypeT = EnumType("PosType", PosType, register = False)
SpaceTypeT = EnumType("SpaceType", SpaceType, register = False)
TeamModeTypeT = EnumType("TeamModeType", TeamModeType, register = False)

## TODO: +/- won't work.
HitFlagTypeF = FlagType("HitFlag", HitFlagType, register = False)
GuardFlagTypeF = FlagType("GuardFlag", GuardFlagType, register = False)

ColorType = TupleType("ColorType", TypeCategory.TUPLE, [IntType, IntType, IntType])
ColorMultType = TupleType("ColorMultType", TypeCategory.TUPLE, [FloatType, FloatType, FloatType])
FloatPairType = TupleType("FloatPairType", TypeCategory.TUPLE, [FloatType, FloatType])
FloatPosType = TupleType("FloatPosType", TypeCategory.TUPLE, [FloatType, FloatType, PosTypeT])
IntPairType = TupleType("IntPairType", TypeCategory.TUPLE, [IntType, IntType])
BoolPairType = TupleType("BoolPairType", TypeCategory.TUPLE, [BoolType, BoolType])
WaveTupleType = TupleType("WaveTupleType", TypeCategory.TUPLE, [IntType, FloatType, FloatType, FloatType])
HitStringType = TupleType("HitStringType", TypeCategory.TUPLE, [HitTypeF, HitAttrF])
PriorityPairType = TupleType("PriorityPairType", TypeCategory.TUPLE, [IntType, PriorityTypeT])
SoundPairType = TupleType("SoundPairType", TypeCategory.TUPLE, [SoundType, IntType])
PeriodicColorType = TupleType("PeriodicColorType", TypeCategory.TUPLE, [IntType, IntType, IntType, IntType])

__all__ = [
    "StructureMember", "StructureType", "EnumType", "FlagType", "TupleType",
    "StateTypeT", "MoveTypeT", "PhysicsTypeT",
    "ColorType", "ColorMultType", "TransTypeT", "AssertTypeT", "FloatPairType",
    "WaveTypeT", "HelperTypeT", "HitFlagTypeF", "GuardFlagTypeF", "TeamTypeT", "HitAnimTypeT",
    "AttackTypeT", "PriorityTypeT", "PosTypeT", "FloatPosType", "IntPairType",
    "WaveTupleType", "HitTypeF", "HitAttrF", "HitStringType", "PriorityPairType",
    "SoundPairType", "PeriodicColorType", "BoolPairType", "TeamModeTypeT",
    "SpaceTypeT"
]