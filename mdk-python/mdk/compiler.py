from typing import Optional, Callable
from functools import partial
import ast
import inspect
import types

from mdk.types.builtins import StateType, MoveType, PhysicsType
from mdk.types.context import StateDefinition, IntExpression, BoolExpression, FloatExpression, Expression
from mdk.types.triggers import TriggerException

from mdk.utils.shared import format_tuple, format_bool, get_context
from mdk.utils.triggers import TriggerAnd, TriggerOr, TriggerNot, TriggerAssign, TriggerPush, TriggerPop

from mdk.stdlib.controllers import ChangeState

def build():
    try:
        ## builds the character from the input data.
        context = get_context()
        for state in context.statedefs:
            definition = context.statedefs[state]
            context.current_state = definition
            definition.fn() # this call registers the controllers in the statedef with the statedef itself.
    except TriggerException as exc:
        print(exc.get_message())

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
        return create_statedef(fn, type, movetype, physics, anim, velset, ctrl, poweradd, juggle, facep2, hitdefpersist, movehitpersist, hitcountpersist, sprpriority, stateno)
    return decorator

## used by the @statedef decorator to create new statedefs,
## but can also be used by character developers to create statedefs ad-hoc (e.g. in a loop).
def create_statedef(
    fn: Callable,
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
    print(f"Discovered a new StateDef named {fn.__name__}. Will process and load this StateDef.")
    # get effective source code of the decorated function
    source, line_number = inspect.getsourcelines(fn)
    location = inspect.getsourcefile(fn)
    # remove decorator lines at the start of the source
    while source[0].strip().startswith('@'):
        source = source[1:]
    source = '\n'.join(source)
    # parse AST from the decorated function
    old_ast = ast.parse(source)
    # use a node transformer to replace any operators we can't override behaviour of (e.g. `and`, `or`, `not`) with function calls
    new_ast = ReplaceLogicalOperators(location, line_number).visit(old_ast)
    #print(ast.dump(new_ast, indent=4))
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
    new_globals["mdk.impl.TriggerPush"] = TriggerPush
    new_globals["mdk.impl.TriggerPop"] = TriggerPop
    # create a new function including these globals.
    new_fn = types.FunctionType(new_code_obj.co_consts[0], new_globals)

    statedef = StateDefinition(new_fn, {}, [])

    # apply each parameter
    if stateno != None: statedef.params["id"] = IntExpression(stateno)
    statedef.params["type"] = Expression(type.name)
    statedef.params["movetype"] = Expression(movetype.name)
    statedef.params["physics"] = Expression(physics.name)
    if anim != None: statedef.params["anim"] = IntExpression(anim)
    if velset != None: statedef.params["velset"] = format_tuple(velset)
    if ctrl != None: statedef.params["ctrl"] = format_bool(ctrl)
    if poweradd != None: statedef.params["poweradd"] = IntExpression(poweradd)
    if juggle != None: statedef.params["juggle"] = IntExpression(juggle)
    if facep2 != None: statedef.params["facep2"] = format_bool(facep2)
    if hitdefpersist != None: statedef.params["hitdefpersist"] = format_bool(hitdefpersist)
    if movehitpersist != None: statedef.params["movehitpersist"] = format_bool(movehitpersist)
    if hitcountpersist != None: statedef.params["hitcountpersist"] = format_bool(hitcountpersist)
    if sprpriority != None: statedef.params["sprpriority"] = IntExpression(sprpriority)

    # add the new statedef to the context
    ctx = get_context()
    ctx.statedefs[fn.__name__] = statedef

    return partial(ChangeState, value = fn.__name__)

class ReplaceLogicalOperators(ast.NodeTransformer):
    def __init__(self, location: Optional[str], line: int):
        self.location = location
        self.line = line

    def visit_Assign(self, node: ast.Assign):
        # if we assign to VariableExpression, IntVar, FloatVar, or BoolVar,
        # the name field needs to be populated.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore
        value = node.value
        if isinstance(node.targets[0], ast.Name) and isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in ["IntVar", "FloatVar", "BoolVar", "VariableExpression"]:
            value.args.append(ast.Constant(
                value=node.targets[0].id
            ))

        return node

    def visit_BoolOp(self, node: ast.BoolOp):
        # inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore
        # get the type of operation: we support transforming AND, OR for boolop.
        if type(node.op) == ast.And:
            target = 'mdk.impl.TriggerAnd'
        elif type(node.op) == ast.Or:
            target = 'mdk.impl.TriggerOr'
        else:
            return node
        
        # add location information as an argument
        node.values.insert(len(node.values), ast.Constant(
                value=self.location
            )
        )
        node.values.insert(len(node.values), ast.Constant(
                value=self.line+node.lineno-1
            )
        )
        
        # then, replace the BoolOp directly with a Call to the appropriate override,
        # with arguments provided from the inner values.
        return ast.Call(
            func=ast.Name(id=target, ctx=ast.Load()),
            args=node.values,
            keywords=[]
        )
    
    def visit_UnaryOp(self, node: ast.UnaryOp):
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore
        # get the type of operation: we support transforming NOT for unaryop
        if type(node.op) == ast.Not:
            target = 'mdk.impl.TriggerNot'
        else:
            return node
        
        # then, replace the BoolOp directly with a Call to the appropriate override,
        # with arguments provided from the inner values.
        return ast.Call(
            func=ast.Name(id=target, ctx=ast.Load()),
            args=[
                node.operand, 
                ast.Constant(
                    value=self.location
                ),
                ast.Constant(
                    value=self.line+node.lineno-1
                )
            ],
            keywords=[]
        )
    
    def visit_NamedExpr(self, node: ast.NamedExpr):
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore
        # then, replace the NamedExpr directly with a Call to the assignment override,
        # with arguments provided from the inner values.
        return ast.Call(
            func=ast.Name(id="mdk.impl.TriggerAssign", ctx=ast.Load()),
            args=[
                ast.Name(id=node.target.id, ctx=ast.Load()),
                node.value,
                ast.Constant(
                    value=self.location
                ),
                ast.Constant(
                    value=self.line+node.lineno-1
                )
            ],
            keywords=[]
        )
    
    def visit_If(self, node: ast.If):
        results: list[ast.If] = []
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore

        # append a call to mdk.impl.TriggerPush at the start of the block,
        # and append a call to mdk.impl.TriggerPop at the end of the block.
        node.body.insert(0, ast.Expr(
            value=ast.Call(
                func=ast.Name(id="mdk.impl.TriggerPush", ctx=ast.Load()),
                args=[
                    ast.Constant(
                        value=self.location
                    ),
                    ast.Constant(
                        value=self.line+node.lineno-1
                    )
                ],
                keywords=[]
            )
        ))
        node.body.insert(len(node.body), ast.Expr(
            value=ast.Call(
                func=ast.Name(id="mdk.impl.TriggerPop", ctx=ast.Load()),
                args=[
                    ast.Constant(
                        value=self.location
                    ),
                    ast.Constant(
                        value=self.line+node.lineno-1
                    )
                ],
                keywords=[]
            )
        ))

        results.append(node)

        # if the 'orelse' block does not start with an 'if' (i.e. is not an 'elif')
        if len(node.orelse) == 1 and isinstance(node.orelse, ast.If):
            ## this is the case for 'elif' blocks.
            ## just pull the If out of the orelse and append it.
            results.append(node.orelse)
            node.orelse = []
        elif len(node.orelse) != 0:
            ## this is the case for 'else' blocks.
            ## we need to wrap these up in another If with the negation of the previous statement.
            new_node = ast.If(
                test=ast.Call(
                    func=ast.Name(id='mdk.impl.TriggerNot', ctx=ast.Load()),
                    args=[
                        node.test,
                        ast.Constant(
                            value=self.location
                        ),
                        ast.Constant(
                            value=self.line+node.lineno-1
                        )
                    ],
                    keywords=[]
                ),
                body=node.orelse,
                orelse=[]
            )
            new_node.body.insert(0, ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="mdk.impl.TriggerPush", ctx=ast.Load()),
                    args=[
                        ast.Constant(
                            value=self.location
                        ),
                        ast.Constant(
                            value=self.line+node.lineno-1
                        )
                    ],
                    keywords=[]
                )
            ))
            new_node.body.insert(len(new_node.body), ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="mdk.impl.TriggerPop", ctx=ast.Load()),
                    args=[
                        ast.Constant(
                            value=self.location
                        ),
                        ast.Constant(
                            value=self.line+node.lineno-1
                        )
                    ],
                    keywords=[]
                )
            ))
            results.append(new_node)
            node.orelse = []

        return results