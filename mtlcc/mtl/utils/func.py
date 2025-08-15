from typing import Optional
from typing import Callable, TypeVar

from ctypes import c_int32

from inspect import getframeinfo, stack

import random
import string

from mtl.types.shared import *
from mtl.types.context import *
from mtl.types.translation import *
from mtl.types.trigger import TriggerTree, TriggerTreeNode
from mtl.types.builtins import BUILTIN_INT, BUILTIN_FLOAT, BUILTIN_BOOL, BUILTIN_STRING, BUILTIN_CINT, BUILTIN_CHAR

def generate_random_string(length: int):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

T = TypeVar('T')
def tryparse(input: str, fn: Callable[[str], T]) -> Optional[T]:
    try:
        return fn(input)
    except:
        return None

def compiler_internal(cc: Optional[CompilerConfiguration]) -> Location:
    if cc != None and cc.no_compiler_internal: return Location("<?>", 0)
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

def match_filenames(f1: str, f2: str) -> Optional[str]:
    ## we want to see if the filenames from `f1` and `f2` match in any way.
    ## we can check a couple ways:
    ### 1. real file match (find the files from paths on disk, confirm they are the same)
    ### 2. stem match (e.g. I input `common1.mtl`, match to `f2` based on last path component)
    if os.path.exists(f1) and os.path.exists(f2):
        return os.path.abspath(f1)
    if os.path.abspath(f2).lower().endswith(f1.lower()):
        ## it's still necessary to find it on the system.
        if os.path.exists(f1): return os.path.abspath(f1)
        if os.path.exists(f2): return os.path.abspath(f2)
    if os.path.abspath(f1).lower().endswith(f2.lower()):
        ## it's still necessary to find it on the system.
        if os.path.exists(f1): return os.path.abspath(f1)
        if os.path.exists(f2): return os.path.abspath(f2)
    return None

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

    if offset == 0 and size == 32:
        return result

    ## access starts from the bit `offset` and progresses to the bit `offset + size`.
    start_pow2 = 2 ** offset
    end_pow2 = 2 ** (offset + size)
    mask = c_int32(end_pow2 - start_pow2)
    result += f" & {mask.value}"

    if offset != 0:
        result = f"floor(({result}) / {c_int32(start_pow2 - 1).value})"

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

def scopes_compatible(s1: StateDefinitionScope, s2: StateDefinitionScope, ctx: TranslationContext) -> bool:
    ## matching
    if s1 == s2:
        return True
    
    ## allow player->shared and helper->shared, but not the reverse
    if s1.type in [StateScopeType.PLAYER, StateScopeType.HELPER] and s2.type == StateScopeType.SHARED:
        return True
    
    ## allow any->target if flagged (this is important for use cases like DEK)
    if s2.type == StateScopeType.TARGET and ctx.compiler_flags.allow_changestate_target:
        return True
    
    return False

def get_redirect_scope(tree: TriggerTree, current: StateDefinitionScope) -> StateDefinitionScope:
    ## tree will be either ATOM or FUNCTION_CALL
    ## we receive current here so we can try and determine the parent/target/etc scope.
    if tree.node == TriggerTreeNode.ATOM:
        ## this will be one of the known trigger expressions.
        if equals_insensitive(tree.operator, "root"):
            ## root will always target the player, unless current scope is TARGET.
            if current.type == StateScopeType.TARGET:
                return StateDefinitionScope(StateScopeType.TARGET, None)
            return StateDefinitionScope(StateScopeType.PLAYER, None)
        elif equals_insensitive(tree.operator, "helper"):
            ## helper must use the generic helper scope as we don't have any more context, unless current scope is TARGET.
            if current.type == StateScopeType.TARGET:
                return StateDefinitionScope(StateScopeType.TARGET, None)
            return StateDefinitionScope(StateScopeType.HELPER, None)
        elif equals_insensitive(tree.operator, "parent"):
            ## TODO: we need to actually determine the parent if possible.
            ## for now assume parent is not knowable and use SHARED, unless current scope is TARGET.
            if current.type == StateScopeType.TARGET:
                return StateDefinitionScope(StateScopeType.TARGET, None)
            return StateDefinitionScope(StateScopeType.SHARED, None)
        elif equals_insensitive(tree.operator, "target"):
            ## target will always use target scope
            ## this would behave weird if you have p2 in a custom state (current scope = target) and use its target redirect.
            ## i think it's a difficult edge case to handle.
            return StateDefinitionScope(StateScopeType.TARGET, None)
        elif equals_insensitive(tree.operator, "partner"):
            ## we don't really support a partner scope, just return shared here.
            ## trying to access partner variables is questionable here anyway.
            ## if current scope is TARGET, then the partner is also TARGET.
            if current.type == StateScopeType.TARGET:
                return StateDefinitionScope(StateScopeType.TARGET, None)
            return StateDefinitionScope(StateScopeType.SHARED, None)
        elif equals_insensitive(tree.operator, "enemy") or equals_insensitive(tree.operator, "enemyNear"):
            ## this will return TARGET, UNLESS the current scope is TARGET, in which case it returns PLAYER.
            ## (because if current scope is TARGET, it means the execution is coming from a custom state,
            ##  and `enemy` is really referring to our player...)
            if current.type == StateScopeType.TARGET:
                return StateDefinitionScope(StateScopeType.PLAYER, None)
            else:
                return StateDefinitionScope(StateScopeType.TARGET, None)
    elif tree.node == TriggerTreeNode.FUNCTION_CALL:
        ## this will be one of the trigger functions, need to determine if we care about the expression or not.
        if equals_insensitive(tree.operator, "target"):
            ## target will always use target scope.
            ## this would behave weird if you have p2 in a custom state (current scope = target) and use its target redirect.
            ## i think it's a difficult edge case to handle.
            return StateDefinitionScope(StateScopeType.TARGET, None)
        elif equals_insensitive(tree.operator, "enemy") or equals_insensitive(tree.operator, "enemyNear"):
            ## this will return TARGET, UNLESS the current scope is TARGET, in which case it returns PLAYER.
            ## (because if current scope is TARGET, it means the execution is coming from a custom state,
            ##  and `enemy` is really referring to our player...)
            if current.type == StateScopeType.TARGET:
                return StateDefinitionScope(StateScopeType.PLAYER, None)
            else:
                return StateDefinitionScope(StateScopeType.TARGET, None)
        elif equals_insensitive(tree.operator, "playerID"):
            ## it's impossible to tell from this trigger which character the redirect targets.
            ## i think it is reasonable to expect developers to use a builtin trigger to 'fix' the scoping.
            return StateDefinitionScope(StateScopeType.SHARED, None)
        elif equals_insensitive(tree.operator, "helper"):
            ## for Helper we need to determine the ID being targeted, if possible.
            ## if it can't be identified (e.g. if the input is an expression), set it to generic Helper scope instead.
            if current.type == StateScopeType.TARGET:
                return StateDefinitionScope(StateScopeType.TARGET, None)
            exprn = tree.children[0]
            if exprn.node == TriggerTreeNode.MULTIVALUE and len(exprn.children) == 1:
                exprn = exprn.children[0]
            if exprn.node == TriggerTreeNode.ATOM and (ival := tryparse(exprn.operator, int)) != None:
                return StateDefinitionScope(StateScopeType.HELPER, ival)
            return StateDefinitionScope(StateScopeType.HELPER, None)

    raise TranslationError(f"Could not determine the target of redirect expression.", tree.location)

def search_file(source: str, includer: str, extra: list[str] = []) -> str:
    search = [
        f"{os.getcwd()}/{source}", 
        f"{os.path.dirname(os.path.realpath(includer))}/{source}", 
        f"{os.path.dirname(os.path.realpath(__file__))}/{source}", 
        f"{os.path.realpath(source)}",
        f"{os.path.dirname(os.path.realpath(__file__))}/stdlib/{source}", 
        f"{os.path.dirname(os.path.realpath(__file__))}/../stdlib/{source}",
        f"{os.path.dirname(os.path.realpath(__file__))}/../{source}"
    ]
    search += extra
    for path in search:
        if os.path.exists(path):
            return path
    raise TranslationError(f"Could not find the source file specified by {source} for inclusion.", compiler_internal(None))

def get_scope(value: str, location: Location) -> StateDefinitionScope:
    if equals_insensitive(value, "shared"):
        return StateDefinitionScope(StateScopeType.SHARED, None)
    elif equals_insensitive(value, "player"):
        return StateDefinitionScope(StateScopeType.PLAYER, None)
    elif equals_insensitive(value, "helper"):
        return StateDefinitionScope(StateScopeType.HELPER, None)
    elif equals_insensitive(value, "target"):
        return StateDefinitionScope(StateScopeType.TARGET, None)
    elif value.lower().startswith("helper(") and value.endswith(")"):
        if (new_target := tryparse(value.split("(")[1].split(")")[0], int)) == None:
            raise TranslationError(f"Could not identify ID for helper scope from input {value}.", location)
        return StateDefinitionScope(StateScopeType.HELPER, new_target)
    raise TranslationError(f"Did not understand scope from input {value}.", location)