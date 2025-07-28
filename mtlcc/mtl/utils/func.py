from typing import Optional
from typing import Callable, TypeVar

from inspect import getframeinfo, stack

import random
import string

from mtl.types.shared import *
from mtl.types.context import *
from mtl.types.translation import *
from mtl.types.builtins import BUILTIN_INT, BUILTIN_FLOAT, BUILTIN_BOOL, BUILTIN_STRING, BUILTIN_CINT, BUILTIN_TYPE

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
            results += make_atom(c.strip())
        return tuple(results)

    if (ivar := tryparse(input, int)) != None:
        return ivar
    elif (fvar := tryparse(input, float)) != None:
        return fvar
    elif input.lower() in ["true", "false"]:
        return input.lower() == "true"
    return input

def parse_builtin(input: str) -> Optional[TypeDefinition]:
    ## parses the input string to see if it matches any built-in type.
    if tryparse(input, int) != None:
        return BUILTIN_INT
    elif tryparse(input, float) != None:
        return BUILTIN_FLOAT
    elif input.lower() in ["true", "false"]:
        return BUILTIN_BOOL
    elif input.startswith('"') and input.endswith('"'):
        return BUILTIN_STRING
    elif len(input) > 1 and input[0] in ["F", "S"] and tryparse(input[1:], int) != None:
        return BUILTIN_CINT
    return None