from typing import Optional
from typing import List, Callable, TypeVar, Union

import os
import random
import string

from inspect import getframeinfo, stack

from mtl.shared import TranslationContext, TypeDefinition, TypeCategory, Location
from mtl.error import TranslationError

def compiler_internal() -> Location:
    caller = getframeinfo(stack()[1][0])
    return Location(caller.filename, caller.lineno)

def generate_random_string(length: int):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def tryParseFloat(input: str) -> Optional[float]:
    try:
        return float(input)
    except ValueError:
        return None
    
def tryParseInt(input: str) -> Optional[int]:
    try:
        return int(input)
    except ValueError:
        return None
    
def tryParseBool(input: str) -> Optional[bool]:
    if input == "true": return True
    elif input == "false": return False
    else: return None

def tryParseCint(input: str) -> Optional[str]:
    # cint: an int with a prefix F or S.
    # special type to support sounds and spark numbers. CNS has very weird syntax.
    if (input.startswith("F") or input.startswith("S")) and tryParseInt(input[1:]):
        return input
    return None

T = TypeVar('T')
def find(l: List[T], p: Callable[[T], bool]) -> Optional[T]:
    result = next(filter(p, l), None)
    return result

## resolves aliases to the target type
def resolveAlias(type: str, ctx: TranslationContext, cycle: List[str]) -> str:
    if type in cycle:
        print("Alias cycle was detected!!")
        print(f"\t-> {type}")
        index = len(cycle) - 1
        while index >= 0:
            print(f"\t-> {cycle[index]}")
            index -= 1
        raise TranslationError("A cycle was detected during alias resolution.", compiler_internal())

    ## if the input type is not an alias, return the input type
    if (alias := find(ctx.types, lambda k: k.name == type and k.category == TypeCategory.ALIAS)) == None:
        return type

    ## otherwise, drill through to the source type
    if (source := find(ctx.types, lambda k: k.name == alias.members[0])) == None:
        raise TranslationError(f"Could not resolve alias from type {type} to {alias.members[0]}", alias.location)
    
    return resolveAlias(source.name, ctx, cycle + [type])

## attempts to convert a concrete type to a union type.
def typeConvertUnion(type1: TypeDefinition, type2: TypeDefinition, ctx: TranslationContext, location: Location) -> Union[TypeDefinition, None]:
    if type2.category != TypeCategory.UNION: return None
    if type1.category == TypeCategory.UNION: return None

    ## iterate each member, resolve alias, and see if the source type is convertible to the member type.
    for member in type2.members:
        unalias = resolveAlias(member, ctx, [])
        resolved = find(ctx.types, lambda k: k.name == unalias)
        if resolved != None and typeConvertOrdered(type1, resolved, ctx, location) != None:
            ## per spec: the union is always assumed to be the wider type during conversion. the output is the union type.
            return type2
        
    ## input type was not convertible to the union member.
    return None

## attempts to convert type1 to type2.
def typeConvertOrdered(type1: TypeDefinition, type2: TypeDefinition, ctx: TranslationContext, location: Location) -> Union[TypeDefinition, None]:
    ## if types match, just return the type.
    if type1.name == type2.name: return type1

    ## this is based on section 1.1 of the spec.

    ## `int` is implicitly convertible to `float`
    if type1.name == "int" and type2.name == "float":
        return type2

    ## `float` cannot be implicitly converted to `int` as it results in loss of precision.
    if type1.name == "float" and type2.name == "int":
        ## in a lot of builtin cases an alternative to convert `int` to `float` will be taken. so just warn and return None.
        ## if no alternative exists an error will be emitted anyway.
        print(f"Warning at {os.path.realpath(location.filename)}:{location.line}: Conversion from float to int may result in loss of precision. If this is intended, use functions like ceil or floor to convert, or explicitly cast one side of the expression.")
        return None
    
    ## smaller builtin types can implicitly convert to wider ones (`bool`->`byte`->`short`->`int`)
    if type1.name in ["bool", "byte", "short"] and type2.name in ["bool", "byte", "short", "int", "float"] and type1.size <= type2.size:
        return type2
    
    ## `char` is implicitly convertible to `byte`, but the reverse is not true.
    if type1.name == "char" and type2.name == "byte":
        return type2
    
    ## the sections related to builtin functions aren't needed.
    ## now resolve for unions.
    if type1.category == TypeCategory.UNION and type2.category != TypeCategory.UNION:
        return typeConvertUnion(type2, type1, ctx, location)
    elif type2.category == TypeCategory.UNION and type1.category != TypeCategory.UNION:
        return typeConvertUnion(type1, type2, ctx, location)

    ## could not convert.
    return None

## attempts to convert type1 to type2, and type2 to type1; returns the widest result.
def typeConvertWidest(type1: TypeDefinition, type2: TypeDefinition, ctx: TranslationContext, location: Location) -> Union[TypeDefinition, None]:
    result1 = typeConvertOrdered(type1, type2, ctx, location)
    result2 = typeConvertOrdered(type1, type2, ctx, location)

    ## only one-way valid conversion? take the other path
    if result1 == None:
        return result2
    if result2 == None:
        return result1
    
    ## otherwise, take the widest
    return result1 if result1.size > result2.size else result2

## unpacks a type (which may be a tuple and may contain repetition or optional syntax) into a list of component types.
def unpackTypes(base_type: str, ctx: TranslationContext) -> Optional[List[TypeDefinition]]:
    result: List[TypeDefinition] = []
    ## each type is delimited with a comma.
    components = [component.strip() for component in base_type.split(",")]
    ## iterate each type and check if it exists.
    ## in this function we do not actually care about the extra syntax, we just want to identify the member types.
    for component in components:
        component = component.replace("?", "").replace("...", "").strip()
        target = find(ctx.types, lambda k: k.name == component)
        if target == None:
            return None
        result.append(target)

    return result

## unpacks two types and compares them. permits for repetition and optionals.
## there is an assumption here that `base_type` is a resolved type and will not contain extra syntax.
def unpackAndMatch(base_type: str, target_type: str, ctx: TranslationContext) -> bool:
    if "," not in base_type and "," not in target_type:
        return base_type == target_type.replace("?", "").replace("...", "")
    ## break each type into its component types
    base_components = [component.strip() for component in base_type.split(",")]
    target_components = [component.strip() for component in base_type.split(",")]
    ## compare component by component until reaching the end of the list, OR the repetition syntax.
    index = 0
    while index < len(base_components) and index < len(target_components):
        ## off the bat just make sure the component type exists
        if find(ctx.types, lambda k: k.name == base_components[index]) == None: return False
        target_type = target_components[index].replace("?", "").replace("...", "")
        ## ensure the current type matches the target
        if base_components[index] != target_type: return False
        ## if the target has the repetition syntax, we should iterate remaining components of base_components and ensure they all match the repeated target.
        if index < len(target_components) and target_components[index].endswith("?"):
            while index < len(base_components):
                if base_components[index] != target_type: return False
                index += 1
            break

        index += 1

    ## if the target type has more components, we need to ensure every additional component has the optional syntax.
    while index < len(target_components):
        if not target_components[index].endswith("?"): return False

    return True