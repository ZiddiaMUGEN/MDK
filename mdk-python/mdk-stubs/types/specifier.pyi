from enum import Enum

class TypeCategory(Enum):
    ENUM = 2
    FLAG = 3
    STRUCTURE = 4
    TUPLE = 20
    BUILTIN = 99

class TypeSpecifier:
    name: str
    category: TypeCategory
    library: str | None
    def __init__(self, name: str, category: TypeCategory) -> None: ...
