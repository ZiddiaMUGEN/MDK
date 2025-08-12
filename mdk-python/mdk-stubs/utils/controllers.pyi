from mdk.types.builtins import BoolType as BoolType, FloatType as FloatType, IntType as IntType, StateNoType as StateNoType, StringType as StringType
from mdk.types.context import CompilerContext as CompilerContext, StateController as StateController
from mdk.types.defined import TupleType as TupleType
from mdk.types.expressions import Expression as Expression, TupleExpression as TupleExpression
from mdk.types.specifier import TypeSpecifier as TypeSpecifier
from mdk.utils.expressions import check_any_assignable as check_any_assignable
from mdk.utils.shared import convert as convert, format_bool as format_bool, format_tuple as format_tuple
from typing import Callable

def controller(**typeinfo) -> Callable[[Callable[..., StateController]], Callable[..., StateController]]: ...
def make_controller(fn, *args, typeinfo: dict[str, list[TypeSpecifier | None]], ignorehitpause: bool | None = None, persistent: int | None = None, **kwargs) -> StateController: ...
