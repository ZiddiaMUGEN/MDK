import traceback
import random
import string
import sys

from mdk.types.errors import CompilationException
from mdk.types.context import CompilerContext
from mdk.types.expressions import Expression
from mdk.types.builtins import BoolType

def generate_random_string(length: int):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def format_tuple(t: tuple) -> Expression:
    return Expression(", ".join(t))

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