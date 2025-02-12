from collections.abc import Callable
from functools import partial
from typing import Optional

import ast
import inspect
import types

from mdk.utils import debug, format_tuple, format_bool
from mdk.types import StateType, MoveType, PhysicsType
from mdk.controllers import ChangeState
from mdk.triggers import TriggerAnd, TriggerOr, TriggerNot, TriggerAssign
from mdk.state import ALL_STATEDEF_IMPLS, StatedefImpl

## Decorator for use with statedefs which accepts optional arguments for each statedef property.
## This returns a partial application of ChangeState, so that user code which calls a declared statedef is compiled to a ChangeState
## (e.g. calling `Walk()` where the function `Walk` is decorated `@statedef` is compiled into a ChangeState).
## something interesting happens in this function to transform logical operators into function calls. this is because the Trigger type can't overload logical operators.
def statedef(
    type: StateType = StateType.U,
    movetype: MoveType = MoveType.U,
    physics: PhysicsType = PhysicsType.U,
    anim: Optional[int] = None,
    velset: Optional[tuple[float, float]] = None,
    ctrl: Optional[bool] = None,
    poweradd: Optional[int] = None,
    juggle: Optional[int] = None,
    facep2: Optional[bool] = None,
    hitdefpersist: Optional[bool] = None,
    movehitpersist: Optional[bool] = None,
    hitcountpersist: Optional[bool] = None,
    sprpriority: Optional[int] = None,
    stateno: Optional[int] = None
) -> Callable:
    def decorator(fn: Callable) -> Callable:
        print(f"Discovered a new StateDef named {fn.__name__}. Will process and load this StateDef.")
        debug(f"Inspecting and modifying AST of function {fn}")
        # get effective source code of the decorated function
        source = inspect.getsource(fn)
        source = '\n'.join(source.splitlines()[1:]) # skip decorator line
        # parse AST from the decorated function
        old_ast = ast.parse(source)
        # use a node transformer to replace any operators we can't override behaviour of (e.g. `and`, `or`, `not`) with function calls
        new_ast = ReplaceLogicalOperators().visit(old_ast)
        # fix location info since the modified nodes won't contain any data
        ast.fix_missing_locations(new_ast)
        # compile the updated AST to a function and use it as the resulting wrapped function.
        new_code_obj = compile(new_ast, fn.__code__.co_filename, 'exec')
        # add missing globals for each operation.
        # these globals are placed into `mdk.impl` namespace to make it easier to identify them in error cases.
        new_globals = fn.__globals__
        new_globals["mdk.impl.TriggerAnd"] = TriggerAnd
        new_globals["mdk.impl.TriggerOr"] = TriggerOr
        new_globals["mdk.impl.TriggerNot"] = TriggerNot
        new_globals["mdk.impl.TriggerAssign"] = TriggerAssign
        # create a new function including these globals.
        new_fn = types.FunctionType(new_code_obj.co_consts[0], new_globals)

        debug(f"Mapping statedef with name {fn.__name__} to function {new_fn}")
        ALL_STATEDEF_IMPLS[fn.__name__] = StatedefImpl(new_fn)

        # apply each parameter
        ALL_STATEDEF_IMPLS[fn.__name__].stateno = stateno
        ALL_STATEDEF_IMPLS[fn.__name__].params["type"] = type.name
        ALL_STATEDEF_IMPLS[fn.__name__].params["movetype"] = movetype.name
        ALL_STATEDEF_IMPLS[fn.__name__].params["physics"] = physics.name
        if anim != None: ALL_STATEDEF_IMPLS[fn.__name__].params["anim"] = str(anim)
        if velset != None: ALL_STATEDEF_IMPLS[fn.__name__].params["velset"] = format_tuple(velset)
        if ctrl != None: ALL_STATEDEF_IMPLS[fn.__name__].params["ctrl"] = format_bool(ctrl)
        if poweradd != None: ALL_STATEDEF_IMPLS[fn.__name__].params["poweradd"] = poweradd
        if juggle != None: ALL_STATEDEF_IMPLS[fn.__name__].params["juggle"] = juggle
        if facep2 != None: ALL_STATEDEF_IMPLS[fn.__name__].params["facep2"] = format_bool(ctrl)
        if hitdefpersist != None: ALL_STATEDEF_IMPLS[fn.__name__].params["hitdefpersist"] = format_bool(hitdefpersist)
        if movehitpersist != None: ALL_STATEDEF_IMPLS[fn.__name__].params["movehitpersist"] = format_bool(movehitpersist)
        if hitcountpersist != None: ALL_STATEDEF_IMPLS[fn.__name__].params["hitcountpersist"] = format_bool(hitcountpersist)
        if sprpriority != None: ALL_STATEDEF_IMPLS[fn.__name__].params["sprpriority"] = sprpriority

        return partial(ChangeState, value = fn.__name__)
    return decorator

class ReplaceLogicalOperators(ast.NodeTransformer):
    def visit_BoolOp(self, node: ast.BoolOp):
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node)
        # get the type of operation: we support transforming AND, OR for boolop.
        if type(node.op) == ast.And:
            target = 'mdk.impl.TriggerAnd'
        elif type(node.op) == ast.Or:
            target = 'mdk.impl.TriggerOr'
        else:
            return node
        
        # then, replace the BoolOp directly with a Call to the appropriate override,
        # with arguments provided from the inner values.
        return ast.Call(
            func=ast.Name(id=target, ctx=ast.Load()),
            args=node.values,
            keywords=[]
        )
    
    def visit_UnaryOp(self, node: ast.UnaryOp):
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node)
        # get the type of operation: we support transforming NOT for unaryop
        if type(node.op) == ast.Not:
            target = 'mdk.impl.TriggerNot'
        else:
            return node
        
        # then, replace the BoolOp directly with a Call to the appropriate override,
        # with arguments provided from the inner values.
        return ast.Call(
            func=ast.Name(id=target, ctx=ast.Load()),
            args=[node.operand],
            keywords=[]
        )
    
    def visit_NamedExpr(self, node: ast.NamedExpr):
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node)
        # then, replace the NamedExpr directly with a Call to the assignment override,
        # with arguments provided from the inner values.
        return ast.Call(
            func=ast.Name(id="mdk.impl.TriggerAssign", ctx=ast.Load()),
            args=[ast.Name(id=node.target.id, ctx=ast.Load()), node.value],
            keywords=[]
        )