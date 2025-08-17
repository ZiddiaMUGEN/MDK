from dataclasses import dataclass

from mdk.types.specifier import TypeCategory, TypeSpecifier
from mdk.types.builtins import *
from mdk.types.expressions import Expression
from mdk.types.context import CompilerContext

## represents a structure member, mapping its field name to a type.
@dataclass
class StructureMember:
    name: str
    type: TypeSpecifier

class StructureType(TypeSpecifier):
    members: list[StructureMember]
    def __init__(self, name: str, members: list[StructureMember]):
        self.name = name
        self.category = TypeCategory.STRUCTURE
        self.members = members

class EnumType(TypeSpecifier):
    members: list[str]
    user_defined: bool
    def __init__(self, name: str, members: list[str], register: bool = True, library: str | None = None):
        self.name = name
        self.category = TypeCategory.ENUM
        self.members = members
        self.user_defined = register

        if register:
            context = CompilerContext.instance()
            if self.name in context.typedefs:
                raise Exception(f"A type with name {self.name} was already registered.")
            context.typedefs[self.name] = self

        self.library = library

    def __getattr__(self, name: str) -> Expression:
        for member in self.members:
            if member == name: return Expression(f"{self.name}.{member}", self)
        raise AttributeError(f"Member {name} does not exist on enum type {self.name}.")
    
class FlagType(TypeSpecifier):
    members: list[str]
    user_defined: bool
    def __init__(self, name: str, members: list[str], register: bool = True, library: str | None = None):
        self.name = name
        self.category = TypeCategory.FLAG
        self.members = members
        self.user_defined = register

        if register:
            context = CompilerContext.instance()
            if self.name in context.typedefs:
                raise Exception(f"A type with name {self.name} was already registered.")
            context.typedefs[self.name] = self

        self.library = library

    def __getattr__(self, name: str) -> Expression:
        all_members: list[str] = []
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
    
StateType = EnumType("StateType", ["S", "C", "A", "L", "U"], register = False)
MoveType = EnumType("MoveType", ["A", "I", "H", "U"], register = False)
PhysicsType = EnumType("PhysicsType", ["S", "C", "A", "N", "U"], register = False)

HitType = FlagType("HitType", ["S", "C", "A"], register = False)
HitAttr = FlagType("HitAttr", ["N", "S", "H", "A", "T", "P"], register = False)

TransType = EnumType("TransType", ["add", "add1", "sub", "none"], register = False)
AssertType = EnumType("AssertType", ["Intro", "Invisible", "RoundNotOver", "NoBarDisplay", "NoBG", "NoFG", "NoStandGuard", "NoCrouchGuard", "NoAirGuard", "NoAutoTurn", "NoJuggleCheck", "NoKOSnd", "NoKOSlow", "NoKO", "NoShadow", "GlobalNoShadow", "NoMusic", "NoWalk", "TimerFreeze", "Unguardable"], register = False)
WaveType = EnumType("WaveType", ["Sine", "Square", "SineSquare", "Off"], register = False)
HelperType = EnumType("HelperType", ["Normal", "Player", "Proj"], register = False)
TeamType = EnumType("TeamType", ["E", "B", "F"], register = False)
HitAnimType = EnumType("HitAnimType", ["Light", "Medium", "Hard", "Back", "Up", "DiagUp"], register = False)
AttackType = EnumType("AttackType", ["High", "Low", "Trip", "None"], register = False)
PriorityType = EnumType("PriorityType", ["Hit", "Miss", "Dodge"], register = False)
PosType = EnumType("PosType", ["P1", "P2", "Front", "Back", "Left", "Right", "None"], register = False)
SpaceType = EnumType("SpaceType", ["Screen", "Stage"], register = False)
TeamModeType = EnumType("TeamModeType", ["Single", "Simul", "Turns"], register = False)

## TODO: +/- won't work.
HitFlagType = FlagType("HitFlagType", ["H", "L", "A", "M", "F", "D", "+", "-"], register = False)
GuardFlagType = FlagType("GuardFlagType", ["H", "L", "A", "M"], register = False)

ColorType = TupleType("ColorType", TypeCategory.TUPLE, [IntType, IntType, IntType])
ColorMultType = TupleType("ColorMultType", TypeCategory.TUPLE, [FloatType, FloatType, FloatType])
FloatPairType = TupleType("FloatPairType", TypeCategory.TUPLE, [FloatType, FloatType])
FloatPosType = TupleType("FloatPosType", TypeCategory.TUPLE, [FloatType, FloatType, PosType])
IntPairType = TupleType("IntPairType", TypeCategory.TUPLE, [IntType, IntType])
BoolPairType = TupleType("BoolPairType", TypeCategory.TUPLE, [BoolType, BoolType])
WaveTupleType = TupleType("WaveTupleType", TypeCategory.TUPLE, [IntType, FloatType, FloatType, FloatType])
HitStringType = TupleType("HitStringType", TypeCategory.TUPLE, [HitType, HitAttr])
PriorityPairType = TupleType("PriorityPairType", TypeCategory.TUPLE, [IntType, PriorityType])
SoundPairType = TupleType("SoundPairType", TypeCategory.TUPLE, [SoundType, IntType])
PeriodicColorType = TupleType("PeriodicColorType", TypeCategory.TUPLE, [IntType, IntType, IntType, IntType])

__all__ = [
    "StructureMember", "StructureType", "EnumType", "FlagType", "TupleType",
    "StateType", "MoveType", "PhysicsType",
    "ColorType", "ColorMultType", "TransType", "AssertType", "FloatPairType",
    "WaveType", "HelperType", "HitFlagType", "GuardFlagType", "TeamType", "HitAnimType",
    "AttackType", "PriorityType", "PosType", "FloatPosType", "IntPairType",
    "WaveTupleType", "HitType", "HitAttr", "HitStringType", "PriorityPairType",
    "SoundPairType", "PeriodicColorType", "BoolPairType", "TeamModeType",
    "SpaceType"
]