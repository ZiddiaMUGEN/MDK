from mdk.types.builtins import *
from dataclasses import dataclass
from mdk.types.expressions import Expression
from mdk.types.specifier import TypeCategory, TypeSpecifier

__all__ = ['StructureMember', 'StructureType', 'EnumType', 'FlagType', 'TupleType', 'StateType', 'MoveType', 'PhysicsType', 'ColorType', 'ColorMultType', 'TransType', 'AssertType', 'FloatPairType', 'WaveType', 'HelperType', 'HitFlagType', 'GuardFlagType', 'TeamType', 'HitAnimType', 'AttackType', 'PriorityType', 'PosType', 'FloatPosType', 'IntPairType', 'WaveTupleType', 'HitType', 'HitAttr', 'HitStringType', 'PriorityPairType', 'SoundPairType', 'PeriodicColorType', 'BoolPairType']

@dataclass
class StructureMember:
    name: str
    type: TypeSpecifier

class StructureType(TypeSpecifier):
    members: list[StructureMember]
    name: str
    category: TypeCategory
    def __init__(self, name: str, members: list[StructureMember]) -> None: ...

class EnumType(TypeSpecifier):
    members: list[str]
    name: str
    category: TypeCategory
    def __init__(self, name: str, members: list[str]) -> None: ...
    def __getattr__(self, name: str) -> Expression: ...

class FlagType(TypeSpecifier):
    members: list[str]
    name: str
    category: TypeCategory
    def __init__(self, name: str, members: list[str]) -> None: ...
    def __getattr__(self, name: str) -> Expression: ...

class TupleType(TypeSpecifier):
    members: list[TypeSpecifier]
    name: str
    category: TypeCategory
    def __init__(self, name: str, category: TypeCategory, members: list[TypeSpecifier]) -> None: ...

StateType: EnumType
MoveType: EnumType
PhysicsType: EnumType
HitType: FlagType
HitAttr: FlagType
TransType: EnumType
AssertType: EnumType
WaveType: EnumType
HelperType: EnumType
TeamType: EnumType
HitAnimType: EnumType
AttackType: EnumType
PriorityType: EnumType
PosType: EnumType
TeamModeType: EnumType
HitFlagType: FlagType
GuardFlagType: FlagType
ColorType: TupleType
ColorMultType: TupleType
FloatPairType: TupleType
FloatPosType: TupleType
IntPairType: TupleType
BoolPairType: TupleType
WaveTupleType: TupleType
HitStringType: TupleType
PriorityPairType: TupleType
SoundPairType: TupleType
PeriodicColorType: TupleType
