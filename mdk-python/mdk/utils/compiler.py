import io
import inspect
import ast
import types
from typing import Callable

from mdk.types.context import StateController, TranslationMode

from mdk.utils.shared import format_bool
from mdk.utils.triggers import TriggerAnd, TriggerOr, TriggerNot, TriggerAssign, TriggerPush, TriggerPop, TriggerPrint

def write_controller(ctrl: StateController, f: io.TextIOWrapper, locations: bool):
    f.write("[State ]\n")
    f.write(f"type = {ctrl.type}\n")
    if len(ctrl.triggers) == 0: ctrl.triggers.append(format_bool(True))
    for trigger in ctrl.triggers:
        f.write(f"trigger1 = {trigger.__str__()}\n")
    for param in ctrl.params:
        f.write(f"{param} = {ctrl.params[param].__str__()}\n")
    if ctrl.location[0] != "<?>" and ctrl.location[1] != 0 and locations:
        f.write(f"mtl.location.file = {ctrl.location[0]}\n")
        f.write(f"mtl.location.line = {ctrl.location[1]}\n")

def rewrite_function(fn: Callable[..., None], overload_print: bool = True, mode: TranslationMode = TranslationMode.STANDARD) -> Callable[..., None]:
    # get effective source code of the decorated function
    source, line_number = inspect.getsourcelines(fn)
    location = inspect.getsourcefile(fn)
    # remove decorator lines at the start of the source
    while source[0].strip().startswith('@'):
        source = source[1:]
    source = ''.join(source)
    # parse AST from the decorated function
    old_ast = ast.parse(source)
    # use a node transformer to replace any operators we can't override behaviour of (e.g. `and`, `or`, `not`) with function calls
    new_ast = ReplaceLogicalOperators(overload_print, mode = mode).visit(old_ast)
    ast.increment_lineno(new_ast, line_number)
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
    new_globals["mdk.impl.TriggerPrint"] = TriggerPrint
    ## find the last code object in the const list.
    new_fn = None
    for index in range(len(new_code_obj.co_consts)):
        if type(new_code_obj.co_consts[index]) == types.CodeType:
            new_fn = types.FunctionType(new_code_obj.co_consts[index], new_globals)
    if new_fn == None:
        raise Exception("Failed to find function code object during template patchup.")
    
    return new_fn

class ReplaceLogicalOperators(ast.NodeTransformer):
    def __init__(self, prints: bool, mode: TranslationMode):
        self.prints = prints
        self.if_depth = 0
        self.mode = mode
        super().__init__()

    def visit_Call(self, node: ast.Call):
        ## if this Call is a print, we want to override with TriggerPrint.
        if not self.prints: return node

        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            node.func.id = "mdk.impl.TriggerPrint"

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
        
        # then, replace the BoolOp directly with a Call to the appropriate override,
        # with arguments provided from the inner values.
        return ast.Call(
            func=ast.Name(id=target, ctx=ast.Load(), lineno=node.lineno, col_offset=node.col_offset),
            args=node.values,
            keywords=[],
            lineno=node.lineno,
            col_offset=node.col_offset
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
            func=ast.Name(id=target, ctx=ast.Load(), lineno=node.lineno, col_offset=node.col_offset),
            args=[
                node.operand
            ],
            keywords=[],
            lineno=node.lineno,
            col_offset=node.col_offset
        )
    
    def visit_NamedExpr(self, node: ast.NamedExpr):
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore
        # then, replace the NamedExpr directly with a Call to the assignment override,
        # with arguments provided from the inner values.
        return ast.Call(
            func=ast.Name(id="mdk.impl.TriggerAssign", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
            args=[
                ast.Name(id=node.target.id, ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                node.value
            ],
            keywords=[],
            lineno=node.lineno,
            col_offset=node.col_offset
        )
    
    def doIf_Standard(self, node: ast.If):
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore

        results: list[ast.stmt] = []

        # append a call to mdk.impl.TriggerPush at the start of the block,
        # and append a call to mdk.impl.TriggerPop at the end of the block.
        node.body.insert(0, ast.Expr(
            value=ast.Call(
                func=ast.Name(id="mdk.impl.TriggerPush", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                args=[
                    ast.Constant(value=None, lineno=node.lineno, col_offset=0)
                ],
                keywords=[],
                lineno=node.lineno,
                col_offset=node.col_offset
            ),
            lineno=node.lineno,
            col_offset=node.col_offset
        ))
        node.body.insert(len(node.body), ast.Expr(
            value=ast.Call(
                func=ast.Name(id="mdk.impl.TriggerPop", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                args=[
                    ast.Constant(value=None, lineno=node.lineno, col_offset=0)
                ],
                keywords=[],
                lineno=node.lineno,
                col_offset=node.col_offset
            ),
            lineno=node.lineno,
            col_offset=node.col_offset
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
                    func=ast.Name(id='mdk.impl.TriggerNot', ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                    args=[
                        node.test
                    ],
                    keywords=[],
                    lineno=node.lineno,
                    col_offset=node.col_offset
                ),
                body=node.orelse,
                orelse=[],
                lineno=node.lineno,
                col_offset=node.col_offset
            )
            new_node.body.insert(0, ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="mdk.impl.TriggerPush", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                    args=[
                        ast.Constant(value=None, lineno=node.lineno, col_offset=0)
                    ],
                    keywords=[],
                    lineno=node.lineno,
                    col_offset=node.col_offset
                ),
                lineno=node.lineno,
                col_offset=node.col_offset
            ))
            new_node.body.insert(len(new_node.body), ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="mdk.impl.TriggerPop", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                    args=[
                        ast.Constant(value=None, lineno=node.lineno, col_offset=0)
                    ],
                    keywords=[],
                    lineno=node.lineno,
                    col_offset=node.col_offset
                ),
                lineno=node.lineno,
                col_offset=node.col_offset
            ))
            results.append(new_node)
            node.orelse = []

        return results
    
    def doIf_Variable(self, node: ast.If):
        self.if_depth += 1
        results: list[ast.stmt] = []
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore

        # append a call to mdk.impl.TriggerPush at the start of the block,
        # and append a call to mdk.impl.TriggerPop at the end of the block.
        node.body.insert(0, ast.Expr(
            value=ast.Call(
                func=ast.Name(id="mdk.impl.TriggerPush", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                args=[
                    ast.Constant(value=self.if_depth, lineno=node.lineno, col_offset=0)
                ],
                keywords=[],
                lineno=node.lineno,
                col_offset=node.col_offset
            ),
            lineno=node.lineno,
            col_offset=node.col_offset
        ))
        node.body.insert(len(node.body), ast.Expr(
            value=ast.Call(
                func=ast.Name(id="mdk.impl.TriggerPop", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                args=[
                    ast.Constant(value=self.if_depth, lineno=node.lineno, col_offset=0)
                ],
                keywords=[],
                lineno=node.lineno,
                col_offset=node.col_offset
            ),
            lineno=node.lineno,
            col_offset=node.col_offset
        ))

        results.append(node)

        ## flatten tree
        ### TODO: `node.orelse` contains either ast.If or other statements.
        ### other statements need to be bundled and dropped into an ast.If as well.
        else_stmt = []
        for stmt in node.orelse:
            if isinstance(stmt, ast.If):
                results.append(stmt)
            else:
                else_stmt.append(stmt)

        if len(else_stmt) > 0:
            results.append(ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="mdk.impl.TriggerPush", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                    args=[
                        ast.Constant(value=-1, lineno=node.lineno, col_offset=0)
                    ],
                    keywords=[],
                    lineno=node.lineno,
                    col_offset=node.col_offset
                ),
                lineno=node.lineno,
                col_offset=node.col_offset
            ))

            results += else_stmt

            results.append(ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="mdk.impl.TriggerPop", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                    args=[
                        ast.Constant(value=None, lineno=node.lineno, col_offset=0)
                    ],
                    keywords=[],
                    lineno=node.lineno,
                    col_offset=node.col_offset
                ),
                lineno=node.lineno,
                col_offset=node.col_offset
            ))

        node.orelse = []

        self.if_depth -= 1
        return results
    
    def visit_If(self, node: ast.If):
        ## if the input function is scoped to TARGET, or is a library (template/trigger) function,
        ## use the safe (non-variable-based) conditional expansion.
        if self.mode == TranslationMode.VARIABLE:
            return self.doIf_Variable(node)
        elif self.mode == TranslationMode.STANDARD:
            return self.doIf_Standard(node)

        