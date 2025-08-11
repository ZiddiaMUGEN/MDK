import traceback
import random
import string
import sys
from typing import Union

from mdk.types.errors import CompilationException
from mdk.types.context import CompilerContext
from mdk.types.expressions import Expression, TupleExpression
from mdk.types.builtins import BoolType, IntType, FloatType, StringType
from mdk.types.defined import TupleType

def convert(input: Union[str, int, float, bool]) -> Expression:
    if isinstance(input, str):
        return Expression(input, StringType)
    elif isinstance(input, int):
        return Expression(str(input), IntType)
    elif isinstance(input, float):
        return Expression(str(input), FloatType)
    elif isinstance(input, bool):
        return Expression("true" if input else "false", BoolType)

def generate_random_string(length: int):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def format_tuple(t: tuple) -> TupleExpression:
    result: list[Expression] = []

    for index in range(len(t)):
        if isinstance(t[index], Expression):
            result.append(t[index])
        else:
            result.append(convert(t[index]))

    return tuple(result)

def convert_tuple(t: tuple, t2: TupleType) -> Expression:
    expression = format_tuple(t)
    return Expression(", ".join([t.exprn for t in expression]), t2) # type: ignore

def format_bool(b: bool) -> Expression:
    return Expression("true" if b else "false", BoolType)

def create_compiler_error(exc: CompilationException):
    context = CompilerContext.instance()
    ## extract the portion of the stack trace that is actually relevant...
    _exc = exc
    if exc.__context__ != None:
        _exc = exc.__context__
    tb = traceback.extract_tb(_exc.__traceback__)
    ## we want to identify the user-side issue (because the traceback contains a bunch of MDK internals as well)
    save_lines: list[str] = []
    for fs in tb:
        for tm in context.templates:
            if context.templates[tm].fn.__name__ == fs.name: save_lines.append(f"{fs.filename}:{fs.lineno}\n\t{fs.line}")
        for sd in context.statedefs:
            if context.statedefs[sd].fn.__name__ == fs.name: save_lines.append(f"{fs.filename}:{fs.lineno}\n\t{fs.line}")
    ## now print full exception and likely causes.
    traceback.print_exception(_exc)
    print()
    print("Likely cause(s) in user-code at:")
    print("\n".join(save_lines))
    print()
    sys.exit(-1)