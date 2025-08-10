from enum import Enum
from dataclasses import dataclass

from mdk.types.expressions import Expression

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

## these are builtin types which must be available to all characters.
IntType = TypeSpecifier("int", TypeCategory.BUILTIN)
FloatType = TypeSpecifier("float", TypeCategory.BUILTIN)
BoolType = TypeSpecifier("bool", TypeCategory.BUILTIN)
ShortType = TypeSpecifier("short", TypeCategory.BUILTIN)
ByteType = TypeSpecifier("byte", TypeCategory.BUILTIN)
CharType = TypeSpecifier("char", TypeCategory.BUILTIN)
StringType = TypeSpecifier("string", TypeCategory.BUILTIN)

StateNoType = TypeSpecifier("stateno", TypeCategory.BUILTIN)

StateType = EnumType("StateType", TypeCategory.ENUM, ["S", "C", "A", "L", "U"])
MoveType = EnumType("MoveType", TypeCategory.ENUM, ["A", "I", "H", "U"])
PhysicsType = EnumType("PhysicsType", TypeCategory.ENUM, ["S", "C", "A", "N", "U"])