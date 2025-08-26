from mdk.types.builtins import *
from dataclasses import dataclass
from mdk.types.expressions import Expression
from mdk.types.specifier import TypeCategory, TypeSpecifier
from enum import Enum, Flag

__all__ = ['StructureMember', 'StructureType', 'EnumType', 'FlagType', 'TupleType', 'StateTypeT', 'MoveTypeT', 'PhysicsTypeT', 'ColorType', 'ColorMultType', 'TransTypeT', 'AssertTypeT', 'FloatPairType', 'WaveTypeT', 'HelperTypeT', 'HitFlagTypeF', 'GuardFlagTypeF', 'TeamTypeT', 'HitAnimTypeT', 'AttackTypeT', 'PriorityTypeT', 'PosTypeT', 'FloatPosType', 'IntPairType', 'WaveTupleType', 'HitTypeF', 'HitAttrF', 'HitStringType', 'PriorityPairType', 'SoundPairType', 'PeriodicColorType', 'BoolPairType', 'SpaceTypeT']

@dataclass
class StructureMember:
    name: str
    type: TypeSpecifier

class StructureType(TypeSpecifier):
    members: list[StructureMember]
    name: str
    category: TypeCategory
    register: bool
    def __init__(self, name: str, members: list[StructureMember], register: bool = True, library: str | None = None) -> None: ...

class EnumType(TypeSpecifier):
    members: list[str]
    name: str
    category: TypeCategory
    register: bool
    library: str | None
    inner_type: type[Enum] | None
    def __init__(self, name: str, members: list[str] | type[Enum], register: bool = True, library: str | None = None) -> None: ...
    def __getattr__(self, name: str) -> Expression: ...

class FlagType(TypeSpecifier):
    members: list[str]
    name: str
    category: TypeCategory
    register: bool
    library: str | None
    inner_type: type[Flag] | None
    def __init__(self, name: str, members: list[str] | type[Flag], register: bool = True, library: str | None = None) -> None: ...
    def __getattr__(self, name: str) -> Expression: ...

class TupleType(TypeSpecifier):
    members: list[TypeSpecifier]
    name: str
    category: TypeCategory
    def __init__(self, name: str, category: TypeCategory, members: list[TypeSpecifier]) -> None: ...

StateTypeT: EnumType
MoveTypeT: EnumType
PhysicsTypeT: EnumType
HitTypeF: FlagType
HitAttrF: FlagType
TransTypeT: EnumType
AssertTypeT: EnumType
WaveTypeT: EnumType
HelperTypeT: EnumType
TeamTypeT: EnumType
HitAnimTypeT: EnumType
AttackTypeT: EnumType
PriorityTypeT: EnumType
PosTypeT: EnumType
SpaceTypeT: EnumType
TeamModeTypeT: EnumType
HitFlagTypeF: FlagType
GuardFlagTypeF: FlagType
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
