from typing import Optional
from typing import List, Callable, TypeVar, Union

import os

from mtl.shared import TranslationContext, TypeDefinition, TypeCategory
from mtl.error import TranslationError

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
        raise TranslationError("A cycle was detected during alias resolution.", "", 0)

    ## if the input type is not an alias, return the input type
    if (alias := find(ctx.types, lambda k: k.name == type and k.category == TypeCategory.ALIAS)) == None:
        return type

    ## otherwise, drill through to the source type
    if (source := find(ctx.types, lambda k: k.name == alias.members[0])) == None:
        raise TranslationError(f"Could not resolve alias from type {type} to {alias.members[0]}", alias.filename, alias.line)
    
    return resolveAlias(source.name, ctx, cycle + [type])

## attempts to convert a concrete type to a union type.
def typeConvertUnion(type1: TypeDefinition, type2: TypeDefinition, ctx: TranslationContext, filename: str, line: int) -> Union[TypeDefinition, None]:
    if type2.category != TypeCategory.UNION: return None
    if type1.category == TypeCategory.UNION: return None

    ## iterate each member, resolve alias, and see if the source type is convertible to the member type.
    for member in type2.members:
        unalias = resolveAlias(member, ctx, [])
        resolved = find(ctx.types, lambda k: k.name == unalias)
        if resolved != None and typeConvertOrdered(type1, resolved, ctx, filename, line) != None:
            ## per spec: the union is always assumed to be the wider type during conversion. the output is the union type.
            return type2
        
    ## input type was not convertible to the union member.
    return None

## attempts to convert type1 to type2.
def typeConvertOrdered(type1: TypeDefinition, type2: TypeDefinition, ctx: TranslationContext, filename: str, line: int) -> Union[TypeDefinition, None]:
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
        print(f"Warning at {os.path.realpath(filename)}:{line}: Conversion from float to int may result in loss of precision. If this is intended, use functions like ceil or floor to convert, or explicitly cast one side of the expression.")
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
        return typeConvertUnion(type2, type1, ctx, filename, line)
    elif type2.category == TypeCategory.UNION and type1.category != TypeCategory.UNION:
        return typeConvertUnion(type1, type2, ctx, filename, line)

    ## could not convert.
    return None

## attempts to convert type1 to type2, and type2 to type1; returns the widest result.
def typeConvertWidest(type1: TypeDefinition, type2: TypeDefinition, ctx: TranslationContext, filename: str, line: int) -> Union[TypeDefinition, None]:
    result1 = typeConvertOrdered(type1, type2, ctx, filename, line)
    result2 = typeConvertOrdered(type1, type2, ctx, filename, line)

    ## only one-way valid conversion? take the other path
    if result1 == None:
        return result2
    if result2 == None:
        return result1
    
    ## otherwise, take the widest
    return result1 if result1.size > result2.size else result2