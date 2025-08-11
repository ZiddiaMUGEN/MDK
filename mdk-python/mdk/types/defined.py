from dataclasses import dataclass

from mdk.types.specifier import TypeCategory, TypeSpecifier
from mdk.types.builtins import *
from mdk.types.expressions import Expression

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
    def __getattr__(self, name: str) -> Expression:
        for member in self.members:
            if member == name: return Expression(f"{self.name}.{member}", self)
        raise AttributeError(f"Member {name} does not exist on enum type {self.name}.")
    
class FlagType(TypeSpecifier):
    members: list[str]
    def __init__(self, name: str, category: TypeCategory, members: list[str]):
        self.name = name
        self.category = category
        self.members = members
    def __getattr__(self, name: str) -> Expression:
        all_members: list[str] = []
        for character in name:
            for member in self.members:
                if member == character: all_members.append(member)
            raise AttributeError(f"Member {character} does not exist on flag type {self.name}.")
        return Expression(f"{self.name}.{name}", self)
    
class TupleType(TypeSpecifier):
    members: list[TypeSpecifier]
    def __init__(self, name: str, category: TypeCategory, members: list[TypeSpecifier]):
        self.name = name
        self.category = category
        self.members = members
    
StateType = EnumType("StateType", TypeCategory.ENUM, ["S", "C", "A", "L", "U"])
MoveType = EnumType("MoveType", TypeCategory.ENUM, ["A", "I", "H", "U"])
PhysicsType = EnumType("PhysicsType", TypeCategory.ENUM, ["S", "C", "A", "N", "U"])

HitType = EnumType("HitType", TypeCategory.FLAG, ["S", "C", "A"])
HitAttr = EnumType("HitAttr", TypeCategory.FLAG, ["N", "S", "H", "A", "T", "P"])

TransType = EnumType("TransType", TypeCategory.ENUM, ["add", "add1", "sub", "none"])
AssertType = EnumType("AssertType", TypeCategory.ENUM, ["Intro", "Invisible", "RoundNotOver", "NoBarDisplay", "NoBG", "NoFG", "NoStandGuard", "NoCrouchGuard", "NoAirGuard", "NoAutoTurn", "NoJuggleCheck", "NoKOSnd", "NoKOSlow", "NoKO", "NoShadow", "GlobalNoShadow", "NoMusic", "NoWalk", "TimerFreeze", "Unguardable"])
WaveType = EnumType("WaveType", TypeCategory.ENUM, ["Sine", "Square", "SineSquare", "Off"])
HelperType = EnumType("HelperType", TypeCategory.ENUM, ["Normal", "Player", "Proj"])
TeamType = EnumType("TeamType", TypeCategory.ENUM, ["E", "B", "F"])
HitAnimType = EnumType("HitAnimType", TypeCategory.ENUM, ["Light", "Medium", "Hard", "Back", "Up", "DiagUp"])
AttackType = EnumType("AttackType", TypeCategory.ENUM, ["High", "Low", "Trip", "None"])
PriorityType = EnumType("PriorityType", TypeCategory.ENUM, ["Hit", "Miss", "Dodge"])
PosType = EnumType("PosType", TypeCategory.ENUM, ["P1", "P2", "Front", "Back", "Left", "Right", "None"])

## TODO: +/- won't work.
HitFlagType = FlagType("HitFlagType", TypeCategory.FLAG, ["H", "L", "A", "M", "F", "D", "+", "-"])
GuardFlagType = FlagType("GuardFlagType", TypeCategory.FLAG, ["H", "L", "A", "M"])

ColorType = TupleType("ColorType", TypeCategory.TUPLE, [IntType, IntType, IntType])
ColorMultType = TupleType("ColorMultType", TypeCategory.TUPLE, [FloatType, FloatType, FloatType])
FloatPairType = TupleType("FloatPairType", TypeCategory.TUPLE, [FloatType, FloatType])
FloatPosType = TupleType("FloatPosType", TypeCategory.TUPLE, [FloatType, FloatType, PosType])
IntPairType = TupleType("IntPairType", TypeCategory.TUPLE, [IntType, IntType])
BoolPairType = TupleType("BoolPairType", TypeCategory.TUPLE, [BoolType, BoolType])
WaveTupleType = TupleType("WaveTupleType", TypeCategory.TUPLE, [IntType, FloatType, FloatType, FloatType])
HitStringType = TupleType("HitStringType", TypeCategory.TUPLE, [IntType, FloatType, FloatType, FloatType])
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
    "SoundPairType", "PeriodicColorType", "BoolPairType"
]