from dataclasses import dataclass

from mdk.types.specifier import TypeCategory, TypeSpecifier
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
    
StateType = EnumType("StateType", TypeCategory.ENUM, ["S", "C", "A", "L", "U"])
MoveType = EnumType("MoveType", TypeCategory.ENUM, ["A", "I", "H", "U"])
PhysicsType = EnumType("PhysicsType", TypeCategory.ENUM, ["S", "C", "A", "N", "U"])

__all__ = ["StructureMember", "StructureType", "EnumType", "FlagType", "StateType", "MoveType", "PhysicsType"]