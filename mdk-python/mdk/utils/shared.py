from mdk.types.context import CompilerContext, Expression, BoolExpression

def format_tuple(t: tuple) -> Expression:
    return Expression(", ".join(t))

def format_bool(b: bool) -> BoolExpression:
    return BoolExpression(b)

## singleton context.
def get_context() -> CompilerContext:
    if not hasattr(CompilerContext, 'instance'):
        return CompilerContext()
    return CompilerContext.instance