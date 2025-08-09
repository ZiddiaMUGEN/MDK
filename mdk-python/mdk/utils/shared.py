from mdk.types.context import CompilerContext, Expression, BoolType

def format_tuple(t: tuple) -> Expression:
    return Expression(", ".join(t))

def format_bool(b: bool) -> Expression:
    return Expression("true" if b else "false", BoolType)

## singleton context.
def get_context() -> CompilerContext:
    if not hasattr(CompilerContext, 'instance'):
        return CompilerContext()
    return CompilerContext.instance