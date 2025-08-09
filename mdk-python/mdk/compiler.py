from typing import Optional, Callable, get_args
from functools import partial
import ast
import inspect
import types
import io
import traceback
import sys

from mdk.types.context import StateDefinition, TemplateDefinition, Expression, StateController, StateType, MoveType, PhysicsType, IntType, TypeSpecifier
from mdk.types.triggers import TriggerException

from mdk.utils.shared import format_tuple, format_bool, get_context
from mdk.utils.triggers import TriggerAnd, TriggerOr, TriggerNot, TriggerAssign, TriggerPush, TriggerPop
from mdk.utils.controllers import make_controller

from mdk.stdlib.controllers import ChangeState

class CompilationException(Exception):
    pass

def build(output: str, skip_templates: bool = False):
    context = get_context()
    try:
        ## builds the character from the input data.
        for state in context.statedefs:
            definition = context.statedefs[state]
            context.current_state = definition
            try:
                definition.fn() # this call registers the controllers in the statedef with the statedef itself.
            except Exception as exc:
                raise CompilationException(exc)
            context.current_state = None

        template_groups = set()
        if not skip_templates and len(context.templates) != 0:
            templates: list[Callable] = []
            for t in context.templates:
                templates.append(context.templates[t].fn)
                if context.templates[t].library == None:
                    context.templates[t].library = output + ".inc"
                template_groups.add(context.templates[t].library)
            library(templates)
        
        with open(output, mode="w") as f:
            if not skip_templates and len(context.templates) != 0:
                for group in template_groups:
                    f.write("[Include]\n")
                    f.write(f"source = {group}\n")
            f.write("\n")
            for name in context.statedefs:
                statedef = context.statedefs[name]
                f.write(f"[Statedef {name}]\n")
                for param in statedef.params:
                    f.write(f"{param} = {statedef.params[param]}\n")
                f.write("\n")
                for controller in statedef.controllers:
                    write_controller(controller, f)
                    f.write("\n")
                f.write("\n")
    except TriggerException as exc:
        print(exc.get_message())
    except CompilationException as exc:
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
        ## now print full exception and likely causes.
        traceback.print_exception(_exc)
        print()
        print("Likely cause(s) in user-code at:")
        print("\n".join(save_lines))
        print()
        sys.exit(-1)
    except Exception as exc:
        print("An internal error occurred while compiling a template, bug the developers.")
        raise exc

def library(templates: list[Callable], output: Optional[str] = None):
    if len(templates) == 0:
        raise Exception("Please specify some templates to be built.")
    context = get_context()
    try:
        per_file: dict[str, list[TemplateDefinition]] = {}
        for template in context.templates:
            definition = context.templates[template]
            context.current_template = definition
            kwargs = {}
            for param in definition.params:
                type = definition.params[param]
                kwargs[param] = Expression(param, type)
            try:
                definition.fn(**kwargs)
            except Exception as exc:
                raise CompilationException(exc)
            context.current_template = None
            if definition.library == None and output == None:
                raise CompilationException(f"Output library was not specified for template {definition.fn.__name__}, either specify a default output in call to library() or specify a library in the template() annotation.")
            if definition.library == None and output != None and definition.fn in templates:
                definition.library = output
            if definition.library not in per_file:
                per_file[definition.library] = [] # type: ignore
            per_file[definition.library].append(definition) # type: ignore

        for group in per_file:
            print(f"Creating output include file {group}.")
            with open(group, mode="w") as f:
                for definition in per_file[group]:
                    f.write("[Define Template]\n")
                    f.write(f"name = {definition.fn.__name__}\n\n")
                    f.write("[Define Parameters]\n")
                    for param in definition.params:
                        f.write(f"{param} = {definition.params[param].name}\n")
                    f.write("\n")
                    for controller in definition.controllers:
                        write_controller(controller, f)
                        f.write("\n")
                    f.write("\n")
    except TriggerException as exc:
        print(exc.get_message())
    except CompilationException as exc:
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
        ## now print full exception and likely causes.
        traceback.print_exception(_exc)
        print()
        print("Likely cause(s) in user-code at:")
        print("\n".join(save_lines))
        print()
        sys.exit(-1)
    except Exception as exc:
        print("An internal error occurred while compiling a template, bug the developers.")
        raise exc

def write_controller(ctrl: StateController, f: io.TextIOWrapper):
    f.write("[State ]\n")
    f.write(f"type = {ctrl.type}\n")
    if len(ctrl.triggers) == 0: ctrl.triggers.append(format_bool(True))
    for trigger in ctrl.triggers:
        f.write(f"trigger1 = {trigger}\n")
    for param in ctrl.params:
        f.write(f"{param} = {ctrl.params[param]}\n")

def statedef(
    type: Expression = StateType.U,
    movetype: Expression = MoveType.U,
    physics: Expression = PhysicsType.U,
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
    type: Expression = StateType.U,
    movetype: Expression = MoveType.U,
    physics: Expression = PhysicsType.U,
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
        line_number -= 1
    source = '\n'.join(source)
    # parse AST from the decorated function
    old_ast = ast.parse(source)
    # use a node transformer to replace any operators we can't override behaviour of (e.g. `and`, `or`, `not`) with function calls
    new_ast = ReplaceLogicalOperators(location, line_number).visit(old_ast)
    #print(ast.dump(new_ast, indent=4))
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
    # create a new function including these globals.
    new_fn = types.FunctionType(new_code_obj.co_consts[0], new_globals)

    statedef = StateDefinition(new_fn, {}, [])

    # apply each parameter
    if stateno != None: statedef.params["id"] = Expression(str(stateno), IntType)
    statedef.params["type"] = type
    statedef.params["movetype"] = movetype
    statedef.params["physics"] = physics
    if anim != None: statedef.params["anim"] = Expression(str(anim), IntType)
    if velset != None: statedef.params["velset"] = format_tuple(velset)
    if ctrl != None: statedef.params["ctrl"] = format_bool(ctrl)
    if poweradd != None: statedef.params["poweradd"] = Expression(str(poweradd), IntType)
    if juggle != None: statedef.params["juggle"] = Expression(str(juggle), IntType)
    if facep2 != None: statedef.params["facep2"] = format_bool(facep2)
    if hitdefpersist != None: statedef.params["hitdefpersist"] = format_bool(hitdefpersist)
    if movehitpersist != None: statedef.params["movehitpersist"] = format_bool(movehitpersist)
    if hitcountpersist != None: statedef.params["hitcountpersist"] = format_bool(hitcountpersist)
    if sprpriority != None: statedef.params["sprpriority"] = Expression(str(sprpriority), IntType)

    # add the new statedef to the context
    ctx = get_context()
    if fn.__name__ in ctx.statedefs:
        raise Exception(f"Attempted to overwrite statedef with name {fn.__name__}.")
    ctx.statedefs[fn.__name__] = statedef

    return partial(ChangeState, value = fn.__name__)

def do_template(name: str, *args, **kwargs) -> StateController:
    def generic_template(*args, **kwargs):
        if len(args) != 0:
            raise Exception("Templates cannot be called with positional arguments, only keyword arguments.")
        result = StateController()
        for arg in kwargs:
            result.params[arg] = kwargs[arg]
        return result
    ctrl = make_controller(generic_template, *args, **kwargs)
    ctrl.type = name
    return ctrl

def template(inputs: list[TypeSpecifier], library: Optional[str] = None) -> Callable:
    def decorator(fn: Callable):
        print(f"Discovered a new Template named {fn.__name__}. Will process and load this Template.")
        # get params of decorated function
        signature = inspect.signature(fn)
        # get effective source code of the decorated function
        source, line_number = inspect.getsourcelines(fn)
        location = inspect.getsourcefile(fn)
        # remove decorator lines at the start of the source
        while source[0].strip().startswith('@'):
            source = source[1:]
            line_number -= 1
        source = '\n'.join(source)
        # parse AST from the decorated function
        old_ast = ast.parse(source)
        # use a node transformer to replace any operators we can't override behaviour of (e.g. `and`, `or`, `not`) with function calls
        new_ast = ReplaceLogicalOperators(location, line_number).visit(old_ast)
        #print(ast.dump(new_ast, indent=4))
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
        # create a new function including these globals.
        ## find the last code object in the const list.
        new_fn = None
        for index in range(len(new_code_obj.co_consts)):
            if type(new_code_obj.co_consts[index]) == types.CodeType:
                new_fn = types.FunctionType(new_code_obj.co_consts[index], new_globals)
        
        if new_fn == None:
            raise Exception("Failed to find function code object during template patchup.")

        if len(signature.parameters) != len(inputs):
            raise Exception(f"Mismatch in template parameter count: saw {len(inputs)} input types, and {len(signature.parameters)} real parameters.")
        params: dict[str, TypeSpecifier] = {}
        index = 0
        for param in signature.parameters:
            params[param] = inputs[index]
            index += 1
        template = TemplateDefinition(new_fn, library, params, [])

        # add the new template to the context
        ctx = get_context()
        if fn.__name__ in ctx.templates:
            raise Exception(f"Attempted to overwrite template with name {fn.__name__}.")
        ctx.templates[fn.__name__] = template

        return partial(do_template, fn.__name__)
    return decorator

class ReplaceLogicalOperators(ast.NodeTransformer):
    def __init__(self, location: Optional[str], line: int):
        self.location = location
        self.line = line

    """
    def visit_Assign(self, node: ast.Assign):
        # if we assign to VariableExpression, IntVar, FloatVar, or BoolVar,
        # the name field needs to be populated.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore
        value = node.value
        if isinstance(node.targets[0], ast.Name) and isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in ["IntVar", "FloatVar", "BoolVar", "VariableExpression"]:
            value.keywords.append(ast.keyword(
                arg="name",
                value=ast.Constant(
                    value=node.targets[0].id,
                    lineno=node.targets[0].lineno,
                    col_offset=node.targets[0].col_offset
                ),
                lineno=node.targets[0].lineno,
                col_offset=node.targets[0].col_offset
            ))

        return node
    """

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
                value=self.location,
                lineno=node.lineno,
                col_offset=node.col_offset
            )
        )
        node.values.insert(len(node.values), ast.Constant(
                value=self.line+node.lineno,
                lineno=node.lineno,
                col_offset=node.col_offset
            )
        )
        
        # then, replace the BoolOp directly with a Call to the appropriate override,
        # with arguments provided from the inner values.
        return ast.Call(
            func=ast.Name(id=target, ctx=ast.Load()),
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
            func=ast.Name(id=target, ctx=ast.Load()),
            args=[
                node.operand, 
                ast.Constant(
                    value=self.location,
                    lineno=node.lineno,
                    col_offset=node.col_offset
                ),
                ast.Constant(
                    value=self.line+node.lineno,
                    lineno=node.lineno,
                    col_offset=node.col_offset
                )
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
                node.value,
                ast.Constant(
                    value=self.location,
                    lineno=node.lineno,
                    col_offset=node.col_offset
                ),
                ast.Constant(
                    value=self.line+node.lineno,
                    lineno=node.lineno,
                    col_offset=node.col_offset
                )
            ],
            keywords=[],
            lineno=node.lineno,
            col_offset=node.col_offset
        )
    
    def visit_If(self, node: ast.If):
        results: list[ast.If] = []
        # recursively inspect child nodes.
        node = super(ReplaceLogicalOperators, self).generic_visit(node) # type: ignore

        # append a call to mdk.impl.TriggerPush at the start of the block,
        # and append a call to mdk.impl.TriggerPop at the end of the block.
        node.body.insert(0, ast.Expr(
            value=ast.Call(
                func=ast.Name(id="mdk.impl.TriggerPush", ctx=ast.Load(), lineno=node.lineno, col_offset=0),
                args=[
                    ast.Constant(
                        value=self.location,
                        lineno=node.lineno,
                        col_offset=node.col_offset
                    ),
                    ast.Constant(
                        value=self.line+node.lineno,
                        lineno=node.lineno,
                        col_offset=node.col_offset
                    )
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
                    ast.Constant(
                        value=self.location,
                        lineno=node.lineno,
                        col_offset=node.col_offset
                    ),
                    ast.Constant(
                        value=self.line+node.lineno,
                        lineno=node.lineno,
                        col_offset=node.col_offset
                    )
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
                        node.test,
                        ast.Constant(
                            value=self.location,
                            lineno=node.lineno,
                            col_offset=node.col_offset
                        ),
                        ast.Constant(
                            value=self.line+node.lineno,
                            lineno=node.lineno,
                            col_offset=node.col_offset
                        )
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
                        ast.Constant(
                            value=self.location,
                            lineno=node.lineno,
                            col_offset=node.col_offset
                        ),
                        ast.Constant(
                            value=self.line+node.lineno,
                            lineno=node.lineno,
                            col_offset=node.col_offset
                        )
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
                        ast.Constant(
                            value=self.location,
                            lineno=node.lineno,
                            col_offset=node.col_offset
                        ),
                        ast.Constant(
                            value=self.line+node.lineno,
                            lineno=node.lineno,
                            col_offset=node.col_offset
                        )
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