from typing import Optional
from typing import Callable, TypeVar

import os

from inspect import getframeinfo, stack
from inspect import currentframe

from mtl.types.shared import Location
from mtl.types.context import TranslationContext
from mtl.types.translation import TypeDefinition, TypeSpecifier, TypeCategory

class TranslationError(Exception):
    message: str

    def __init__(self, message: str, location: Location):
        super().__init__(f"Translation error at {os.path.realpath(location.filename)}:{location.line}: {message}")
        self.message = f"{os.path.realpath(location.filename)}:{location.line}: {message}"

def line_number() -> int:
    cf = currentframe()
    if cf != None and cf.f_back != None:
        return cf.f_back.f_lineno
    else:
        return 0

def compiler_internal() -> Location:
    caller = getframeinfo(stack()[1][0])
    return Location(caller.filename, caller.lineno)

T = TypeVar('T')
def find(l: list[T], p: Callable[[T], bool]) -> Optional[T]:
    result = next(filter(p, l), None)
    return result

def find_type(type_name: str, ctx: TranslationContext) -> Optional[TypeDefinition]:
    return find(ctx.types, lambda k: k.name == type_name)

def resolve_alias(type: str, ctx: TranslationContext, loc: Location) -> str:
    ## recursively reduces an alias to its target type
    target_type = find_type(type, ctx)
    if target_type == None:
        ## we return the input here because it's possible `type` is a type-string (such as int,int,float)
        return type
    if target_type.category != TypeCategory.ALIAS:
        return target_type.name
    return resolve_alias(target_type.members[0], ctx, loc)

def unpack_types(type: str, ctx: TranslationContext, loc: Location) -> list[TypeSpecifier]:
    ## unpacks types in the form `t1,t2,t3` (multi-value types)
    ## additionally handles optional and repetition syntax
    result: list[TypeSpecifier] = []

    type = resolve_alias(type, ctx, loc)

    for subtype in type.split(","):
        subtype = subtype.strip()

        required = not subtype.endswith("?")
        subtype = subtype.replace("?", "")
        repeated = subtype.endswith("...")
        subtype = subtype.replace("...", "")

        ## need to re-resolve aliases here!
        ## what happens if the re-resolved alias is another packed type string? everything breaks!
        subtype = resolve_alias(subtype, ctx, loc)

        if (subtype_definition := find_type(subtype, ctx)) == None:
            raise TranslationError(f"Could not find a type with name {subtype}", loc)
        
        result.append(TypeSpecifier(subtype_definition, required, repeated))

    return result