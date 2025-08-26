from enum import Enum
from typing import Optional

## this specifies a subset of the type categories provided by MTL.
class TypeCategory(Enum):
    #INVALID = -1
    #ALIAS = 0
    #UNION = 1
    ENUM = 2
    FLAG = 3
    STRUCTURE = 4
    TUPLE = 20
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
    library: Optional[str]
    register: bool
    def __init__(self, name: str, category: TypeCategory, register: bool = True):
        self.name = name
        self.category = category
        self.library = None
        self.register = register