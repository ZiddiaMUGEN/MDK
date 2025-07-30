from typing import Optional
from typing import Callable, TypeVar

from ctypes import c_int32

from inspect import getframeinfo, stack

import random
import string

from mtl.types.shared import *
from mtl.types.context import *
from mtl.types.translation import *
from mtl.types.builtins import BUILTIN_INT, BUILTIN_FLOAT, BUILTIN_BOOL, BUILTIN_STRING, BUILTIN_CINT, BUILTIN_CHAR

def generate_random_string(length: int):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

T = TypeVar('T')
def tryparse(input: str, fn: Callable[[str], T]) -> Optional[T]:
    try:
        return fn(input)
    except:
        return None

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

def includes_insensitive(s1: str, s2: list[str]) -> bool:
    incl = [s.lower() for s in s2]
    return s1.lower() in incl

def make_atom(input: str) -> Any:
    if "," in input:
        results: list[Any] = []
        for c in input.split(","):
            results.append(make_atom(c.strip()))
        return tuple(results)

    if (ivar := tryparse(input, int)) != None:
        return ivar
    elif (fvar := tryparse(input, float)) != None:
        return fvar
    elif input.lower() in ["true", "false"]:
        return input.lower() == "true"
    return input

def parse_builtin(input: str) -> Optional[Expression]:
    ## parses the input string to see if it matches any built-in type.
    if tryparse(input, int) != None:
        return Expression(BUILTIN_INT, input)
    elif tryparse(input, float) != None:
        return Expression(BUILTIN_FLOAT, input)
    elif input.lower() in ["true", "false"]:
        return Expression(BUILTIN_BOOL, "1" if input.lower() == "true" else "0")
    elif input.startswith("'") and input.endswith("'") and len(input) == 3:
        return Expression(BUILTIN_CHAR, str(ord(input[1])))
    elif input.startswith('"') and input.endswith('"'):
        return Expression(BUILTIN_STRING, input)
    elif len(input) > 1 and input[0] in ["F", "S"] and tryparse(input[1:], int) != None:
        return Expression(BUILTIN_CINT, input)
    return None

def mask_variable(index: int, offset: int, size: int, is_float: bool) -> str:
    ## takes information describing the location of a variable in `var`-space,
    ## and creates a string which accesses that variable.
    result = f"var({index})"
    if is_float: result = f"f{result}"

    if offset != 0:
        ## access starts from the bit `offset` and progresses to the bit `offset + size`.
        start_pow2 = 2 ** offset
        end_pow2 = 2 ** (offset + size)
        mask = c_int32(end_pow2 - start_pow2)
        result += f" & {mask.value}"

    return result

def mask_write(index: int, exprn: str, offset: int, size: int, is_float: bool) -> str:
    ## takes information describing the location of a variable in `var`-space,
    ## and modifies an expression to write to the correct location for that var.
    if offset == 0 and size == 32:
        return exprn
    
    ## we need to make sure the values of the var that fall outside the range are preserved.
    indexed = f"var({index})"
    if is_float: indexed = f"f{indexed}"
    
    ## we need to clamp the expression to `size`, then bit-shift the expression up to `offset`.
    exprn = f"((({exprn}) & {(2 ** size) - 1}) * {c_int32(2 ** offset).value})"

    mask = 0

    ## left-hand-side of the range: everything from (offset + size) -> 32
    if (offset + size) < 32:
        start_pow2 = 2 ** (offset + size)
        end_pow2 = 2 ** 33
        mask += end_pow2 - start_pow2

    ## right-hand-side of the range: everything from 0 -> offset
    if offset > 0:
        mask += (2 ** offset) - 1
    
    if mask != 0:
        exprn = f"({exprn} + ({indexed} & {c_int32(mask).value}))"

    return exprn

def scopes_compatible(s1: StateDefinitionScope, s2: StateDefinitionScope) -> bool:
    ## matching
    if s1 == s2:
        return True
    
    ## allow player->shared and helper->shared, but not the reverse
    if s1.type in [StateScopeType.PLAYER, StateScopeType.HELPER] and s2.type == StateScopeType.SHARED:
        return True
    
    return False