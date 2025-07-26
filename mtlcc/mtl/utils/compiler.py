from typing import Optional
from typing import Callable, TypeVar

import os

from inspect import getframeinfo, stack
from inspect import currentframe

from mtl.types.shared import Location
from mtl.types.context import TranslationContext
from mtl.types.translation import *

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

def get_all(l: list[T], p: Callable[[T], bool]) -> list[T]:
    result = list(filter(p, l))
    return result

def equals_insensitive(s1: str, s2: str) -> bool:
    return s1.lower() == s2.lower()

def find_type(type_name: str, ctx: TranslationContext) -> Optional[TypeDefinition]:
    return find(ctx.types, lambda k: equals_insensitive(k.name, type_name))

def find_trigger(trigger_name: str, param_types: list[TypeDefinition], ctx: TranslationContext) -> Optional[TriggerDefinition]:
    all_matches = get_all(ctx.triggers, lambda k: equals_insensitive(k.name, trigger_name))
    ## there may be multiple candidate matches, we need to check if the types provided as input match the types of the candidate.
    for match in all_matches:
        ## the input type count should exactly match.
        ## we do not support optional arguments for triggers yet.
        if len(param_types) != len(match.params): continue
        matched = True
        for index in range(len(param_types)):
            if get_type_match(param_types[index], match.params[index].type, ctx) == None:
                matched = False
        ## if no types failed to match, we can return this type as the signature matches
        if matched: 
            return match
    ## if we reach here, no matching signature was found
    return None

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

def get_widest_match(t1: TypeDefinition, t2: TypeDefinition, ctx: TranslationContext) -> Optional[TypeDefinition]:
    ## match t1 to t2, accepting any widening conversion which allows the types to match.
    wide1 = get_type_match(t1, t2, ctx)
    wide2 = get_type_match(t2, t1, ctx)

    if wide1 != None and wide2 != None:
        ## if both conversions work, return the widest
        return wide1 if wide1.size >= wide2.size else wide2
    elif wide1 != None and wide2 == None:
        ## return the only working conversion
        return wide1
    elif wide1 == None and wide2 != None:
        ## return the only working conversion
        return wide2
    else:
        ## neither conversion worked, types are not compatible
        return None

def get_type_match(t1: TypeDefinition, t2: TypeDefinition, ctx: TranslationContext) -> Optional[TypeDefinition]:
    ## match t1 to t2, following type conversion rules.
    ## if types match, t1 return the type.
    if t1 == t2: return t1

    ## this is based on section 1.1 of the spec.

    ## `int` is implicitly convertible to `float`
    if t1.name == "int" and t2.name == "float":
        return t2

    ## `float` cannot be implicitly converted to `int` as it results in loss of precision.
    if t1.name == "float" and t2.name == "int":
        ## in a lot of builtin cases an alternative to convert `int` to `float` will be taken. so just warn and return None.
        ## if no alternative exists an error will be emitted anyway.
        print(f"Warning: Conversion from float to int may result in loss of precision. If this is intended, use functions like ceil or floor to convert, or explicitly cast one side of the expression.")
        return None
    
    ## smaller builtin types can implicitly convert to wider ones (`bool`->`byte`->`short`->`int`)
    if t1.name in ["bool", "byte", "short"] and t2.name in ["bool", "byte", "short", "int"] and t1.size <= t2.size:
        return t2
    
    ## `char` is implicitly convertible to `byte`, but the reverse is not true.
    if t1.name == "char" and t2.name == "byte":
        return t2
    
    ## it's permitted to 'widen' a concrete type to a union type if the union type has a matching member
    if t2.category == TypeCategory.UNION:
        for member in t2.members:
            if (target_type := find_type(member, ctx)) != None and (widened := get_type_match(t1, target_type, ctx)) != None:
                return widened

    ## could not convert.
    return None